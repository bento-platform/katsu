import datetime

from calendar import month_abbr
from collections import Counter, defaultdict
from django.db.models import Case, CharField, Count, F, Func, IntegerField, Model, QuerySet, When, Value
from django.db.models.functions import Cast
from typing import Any, Mapping, Type

from ..logger import logger

from . import fields_utils as f_utils
from .censorship import get_threshold, thresholded_count
from .fields_utils import monthly_generator
from .model_lookups import PUBLIC_MODEL_NAMES_TO_MODEL
from .stats import stats_for_field
from .types import BinWithValue

LENGTH_Y_M = 4 + 1 + 2  # dates stored as yyyy-mm-dd


def get_public_model_name_and_field_path(field_id: str) -> tuple[str, tuple[str, ...]]:
    model_name, *field_path = field_id.split("/")
    return model_name, tuple(field_path)


def get_model_and_field(field_id: str) -> tuple[Type[Model], str]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of the model object and the Django string representation of the
    field for this object.
    """

    model_name, field_path = get_public_model_name_and_field_path(field_id)

    model: Type[Model] | None = PUBLIC_MODEL_NAMES_TO_MODEL.get(model_name)
    if model is None:
        msg = f"Accessing field on model {model_name} not implemented"
        raise NotImplementedError(msg)

    field_name = "__".join(field_path)
    return model, field_name


async def get_field_bins(query_set: QuerySet, field: str, bin_size: int):
    # computes a new column "binned" by substracting the modulo by bin size to
    # the value which requires binning (e.g. 28 => 28 - 28 % 10 = 20)
    # cast to integer to avoid numbers such as 60.00 if that was a decimal,
    # and aggregate over this value.
    query_set = query_set.annotate(
        binned=Cast(
            F(field) - Func(F(field), bin_size, function="MOD"),
            IntegerField()
        )
    ).values("binned").annotate(total=Count("binned"))
    stats = {item["binned"]: item["total"] async for item in query_set}
    return stats


async def get_field_options(field_props: dict, low_counts_censored: bool) -> list[Any]:
    """
    Given properties for a public field, return the list of authorized options for
    querying this field.
    """
    if field_props["datatype"] == "string":
        options = field_props["config"].get("enum")
        # Special case: no list of values specified
        if options is None:
            # We must be careful here not to leak 'small cell' values as options
            # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
            #   should be treated as if the field isn't in the database at all.
            options = await get_distinct_field_values(field_props, low_counts_censored)
    elif field_props["datatype"] == "number":
        options = [label for floor, ceil, label in f_utils.labelled_range_generator(field_props)]
    elif field_props["datatype"] == "date":
        # Assumes the field is in extra_properties, thus can not be aggregated
        # using SQL MIN/MAX functions
        start, end = await get_month_date_range(field_props)
        options = [
            f"{month_abbr[m].capitalize()} {y}" for y, m in f_utils.monthly_generator(start, end)
        ] if start else []
    else:
        raise NotImplementedError()

    return options


async def get_distinct_field_values(field_props: dict, low_counts_censored: bool) -> list[Any]:
    # We must be careful here not to leak 'small cell' values as options
    # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
    #   should be treated as if the field isn't in the database at all.

    model, field = get_model_and_field(field_props["mapping"])
    threshold = get_threshold(low_counts_censored)

    return [
        val
        async for val, count in (
            model.objects
            .values_list(field)
            .annotate(count=Count(field))
        )
        if count > threshold
    ]


async def compute_binned_ages(individual_queryset: QuerySet, bin_size: int) -> list[int]:
    """
    When age_numeric field is not available, use this function to process
    the age field in its various formats.
    Params:
        - individual_queryset: a queryset made on the individual model, containing
            the age and age_numeric fields
        - bin_size: how many years there is per bin
    Returns a list of values floored to the closest decade (e.g. 25 --> 20)
    """

    a = individual_queryset.filter(age_numeric__isnull=True).values('time_at_last_encounter')
    binned_ages = []
    async for r in a:
        if r["time_at_last_encounter"] is None:
            continue
        age = f_utils.parse_individual_age(r["time_at_last_encounter"])
        binned_ages.append(age - age % bin_size)

    return binned_ages


async def get_age_numeric_binned(individual_queryset: QuerySet, bin_size: int, low_counts_censored: bool) -> dict:
    """
    age_numeric is computed at ingestion time of phenopackets. On some instances
    it might be unavailable and as a fallback must be computed from the age JSON field which
    has two alternate formats (hence more complex and slower to process)
    """
    individuals_age = await get_field_bins(individual_queryset, "age_numeric", bin_size)
    if None not in individuals_age:
        return individuals_age

    del individuals_age[None]
    individuals_age = Counter(individuals_age)
    individuals_age.update(
        # single update instead of creating iterables in a loop
        await compute_binned_ages(individual_queryset, bin_size)
    )

    return {
        b: thresholded_count(bv, low_counts_censored)
        for b, bv in individuals_age.items()
    }


async def get_month_date_range(field_props: dict) -> tuple[str | None, str | None]:
    """
    Get start date and end date from the database
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Aggregate functions
    are not available for data in JSON fields.
    Implement handling dates as regular fields when needed.
    TODO: for now only dates binned by month are handled.
    """

    if (bin_by := field_props["config"]["bin_by"]) != "month":
        raise NotImplementedError(f"Binning dates by `{bin_by}` method not implemented")

    model, field_name = get_model_and_field(field_props["mapping"])

    if "extra_properties" not in field_name:
        raise NotImplementedError("Binning date-like fields that are not in extra_properties is not implemented")

    is_not_null_filter = {f"{field_name}__isnull": False}   # property may be missing: avoid handling "None"

    # Note: lexicographic sort is correct with date strings like `2021-03-09`
    query_set = (
        model.objects
        .filter(**is_not_null_filter)
        .values(field_name)
        .distinct()
        .order_by(field_name)
    )

    if (await query_set.acount()) == 0:
        return None, None

    start = (await query_set.afirst())[field_name][:LENGTH_Y_M]
    end = (await query_set.alast())[field_name][:LENGTH_Y_M]

    return start, end


async def get_range_stats(field_props: dict, low_counts_censored: bool = True) -> list[BinWithValue]:
    model, field = get_model_and_field(field_props["mapping"])

    # Generate a list of When conditions that return a label for the given bin.
    # This is equivalent to an SQL CASE statement.
    whens = [
        When(
            **{f"{field}__gte": floor} if floor is not None else {},
            **{f"{field}__lt": ceil} if ceil is not None else {},
            then=Value(label),
        )
        for floor, ceil, label in f_utils.labelled_range_generator(field_props)
    ]

    query_set = (
        model.objects
        .values(label=Case(*whens, default=Value("missing"), output_field=CharField()))
        .annotate(total=Count("label"))
    )

    # Maximum number of entries needed to round a count from its true value down to 0 (censored discovery)
    stats: dict[str, int] = dict()
    async for item in query_set:
        stats[item["label"]] = thresholded_count(item["total"], low_counts_censored)

    # All the bins between start and end must be represented and ordered
    bins: list[BinWithValue] = [
        {"label": label, "value": stats.get(label, 0)}
        for floor, ceil, label in f_utils.labelled_range_generator(field_props)
    ]

    if "missing" in stats:
        bins.append({"label": "missing", "value": stats["missing"]})

    return bins


async def get_categorical_stats(field_props: dict, low_counts_censored: bool) -> list[BinWithValue]:
    """
    Fetches statistics for a given categorical field and apply privacy policies
    """

    model, field_name = get_model_and_field(field_props["mapping"])

    stats: Mapping[str, int] = await stats_for_field(model, field_name, add_missing=True)

    # Enforce values order from config and apply policies
    labels: list[str] | None = field_props["config"].get("enum")
    derived_labels: bool = labels is None

    # Special case: for some fields, values are based on what's present in the
    # dataset (enum is null in the public JSON).
    # - Here, apply lexical sort, and exclude the "missing" value which will
    #   be appended at the end if it is set.
    # - Note that in this situation, we explictly MUST remove rounded-down 0-counts
    #   (below the threshold) below, otherwise we LEAK that there is 1 <= x <= threshold
    #   matching entries in the DB.
    if derived_labels:
        labels = sorted(
            [k for k in stats.keys() if k != "missing"],
            key=lambda x: x.lower()
        )

    bins: list[BinWithValue] = []

    for category in labels:
        # Censor small counts by rounding them to 0
        v: int = thresholded_count(stats.get(category, 0), low_counts_censored)

        if v == 0 and derived_labels:
            # We cannot append 0-counts for derived labels, since that indicates
            # there is a non-0 count for this label in the database - i.e., if the label is pulled
            # from the values in the database, someone could otherwise learn 1 <= this field <= threshold
            # given it being present at all.
            continue

            # Otherwise (pre-made labels, so we aren't leaking anything), keep the 0-count.

        bins.append({"label": category, "value": v})

    if stats["missing"]:
        bins.append({"label": "missing", "value": stats["missing"]})

    return bins


async def get_date_stats(field_props: dict, low_counts_censored: bool = True) -> list[BinWithValue]:
    """
    Fetches statistics for a given date field, fill the gaps in the date range
    and apply privacy policies.
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Handle dates as
     regular fields when needed.
    TODO: for now only dates binned by month are handled
    """

    if (bin_by := field_props["config"]["bin_by"]) != "month":
        msg = f"Binning dates by `{bin_by}` method not implemented"
        raise NotImplementedError(msg)

    model, field_name = get_model_and_field(field_props["mapping"])

    if "extra_properties" not in field_name:
        msg = "Binning date-like fields that are not in extra-properties is not implemented"
        raise NotImplementedError(msg)

    # Note: lexical sort works on ISO dates
    query_set = (
        model.objects
        .values(field_name)
        .order_by(field_name)
        .annotate(total=Count(field_name))
    )

    stats = defaultdict(int)
    start: str | None = None
    end: str | None = None
    # Key the counts on yyyy-mm combination (aggregate same month counts)
    async for item in query_set:
        key = "missing" if item[field_name] is None else item[field_name][:LENGTH_Y_M]
        stats[key] += item["total"]

        if key == "missing":
            continue

        # start is set to the first non-missing key processed; end is set to the last one.
        if start:
            end = key
        else:
            start = key

    # All the bins between start and end date must be represented
    bins: list[BinWithValue] = []
    if start:   # at least one month
        for year, month in monthly_generator(start, end or start):
            key = f"{year}-{month:02d}"
            label = f"{month_abbr[month].capitalize()} {year}"    # convert key as yyyy-mm to `abbreviated month yyyy`
            bins.append({
                "label": label,
                "value": thresholded_count(stats.get(key, 0), low_counts_censored),
            })

    # Append missing items at the end if any
    if "missing" in stats:
        bins.append({"label": "missing", "value": thresholded_count(stats["missing"], low_counts_censored)})

    return bins


def filter_queryset_field_value(qs: QuerySet, field_props, value: str):
    """
    Further filter a queryset using the field defined by field_props and the
    given value.
    It is a prerequisite that the field mapping defined in field_props is represented
    in the queryset object.
    `mapping_for_search_filter` is an optional property that gets precedence over `mapping`
    for the necessity of filtering. It is not necessary to specify this when
    the `mapping` value is based on the same model as the queryset.
    """

    model, field = get_model_and_field(
        field_props["mapping_for_search_filter"] if "mapping_for_search_filter" in field_props
        else field_props["mapping"]
    )

    if field_props["datatype"] == "string":
        condition = {f"{field}__iexact": value}
    elif field_props["datatype"] == "number":
        # values are of the form "[50, 150)", "< 50" or "≥ 800"

        if value.startswith("["):
            [start, end] = [int(v) for v in value.lstrip("[").rstrip(")").split(", ")]
            condition = {
                f"{field}__gte": start,
                f"{field}__lt": end
            }
        else:
            [sym, val] = value.split(" ")
            if sym == "≥":
                condition = {f"{field}__gte": int(val)}
            elif sym == "<":
                condition = {f"{field}__lt": int(val)}
            else:
                raise NotImplementedError()
    elif field_props["datatype"] == "date":
        # For now, limited to date expressed as month/year such as "May 2022"
        d = datetime.datetime.strptime(value, "%b %Y")
        val = d.strftime("%Y-%m")   # convert to "yyyy-mm" format to search for dates as "2022-05-03"
        condition = {f"{field}__startswith": val}
    else:
        raise NotImplementedError()

    logger.debug(f"Filtering {model}.{field} with {condition}")

    return qs.filter(**condition)
