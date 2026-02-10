import datetime
import re

from bento_lib.discovery import (
    DiscoveryConfig, DateFieldDefinition, FieldDefinition, NumberFieldDefinition, StringFieldDefinition, DiscoveryEntity
)
from calendar import month_abbr
from collections import Counter, defaultdict

from chord_metadata_service.discovery.censorship import get_threshold
from django.db.models import Case, CharField, Count, F, Func, IntegerField, QuerySet, When, Value, Q, Exists, OuterRef
from django.db.models.functions import Cast
from structlog.stdlib import BoundLogger
from typing import Any, Mapping

from chord_metadata_service.authz.types import DataPermissions

from . import fields_utils as f_utils
from .censorship import censor_count, thresholded_count
from .field_paths.django_field_query import DiscoveryFieldSubquery, get_field_django_mapping_and_queried_entity
from .scope import ValidatedDiscoveryScope
from .pydantic_models import BinWithValue, BinList
from .stats import stats_for_field

LENGTH_Y_M = 4 + 1 + 2  # dates stored as yyyy-mm-dd

# Number range patterns
BEGIN_RANGE_PATTERN = re.compile(r"(?P<sym>[<≤]) (?P<val>-?\d+(\.\d+)?)")
MIDDLE_RANGE_PATTERN = re.compile(
    r"(?P<start_sym>[\[(>≥])(?P<start>-?\d+(\.\d+)?), (?P<end>-?\d+(\.\d+)?)(?P<end_sym>[])<≤])"
)
END_RANGE_PATTERN = re.compile(r"(?P<sym>[>≥]) (?P<val>-?\d+(\.\d+)?)")


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


async def get_field_options(
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    field_id: str,
    scope: ValidatedDiscoveryScope,
    field_permissions: DataPermissions,
) -> list[Any]:
    """
    Given properties for a public field, return the list of authorized options for
    querying this field.
    """

    field_props = scope.discovery.fields[field_id]
    threshold = get_threshold(scope, field_permissions)

    if field_props.datatype == "string":
        options = getattr(field_props.config, "enum", None)
        # Special case: no list of values specified
        if options is None:
            # We must be careful here not to leak 'small cell' values as options
            # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
            #   should be treated as if the field isn't in the database at all.
            options = await get_distinct_field_values(queryset_entity, queryset, field_props, threshold)
    elif field_props.datatype == "number":
        options = [label for floor, ceil, label in f_utils.labelled_range_generator(field_props)]
    elif field_props.datatype == "date":
        # Assumes the field is in extra_properties, thus can not be aggregated
        # using SQL MIN/MAX functions
        start, end = await get_month_date_range(queryset_entity, queryset, field_props, threshold)
        options = [
            # TODO: need to pass a threshold to monthly range generator
            f"{month_abbr[m].capitalize()} {y}" for y, m in f_utils.monthly_generator(start, end)
        ] if start else []
    else:  # pragma: no cover
        # Can't actually occur with Pydantic implementation of the discovery configuration model, which will validate
        # the data_type value.
        raise NotImplementedError()

    return options


async def get_distinct_field_values(
    queryset_entity: DiscoveryEntity, queryset: QuerySet, field_props: FieldDefinition, threshold: int
) -> list[str]:
    # We must be careful here not to leak 'small cell' values as options
    # - e.g., if there are three individuals with sex=UNKNOWN_SEX, this
    #   should be treated as if the field isn't in the database at all.

    mapping_field = f_utils.get_field_django_mapping(queryset_entity, field_props)

    field_query = mapping_field
    if gb := field_props.group_by:
        # JSONField containing an array
        # use jsonb_path_query field expression
        field_query = f_utils.get_jsonb_path_query(mapping_field, gb)

    values_with_counts = queryset.values_list(field_query).annotate(count=Count(mapping_field))

    res = [
        str(val)  # should already be a string, since get_distinct_field_values is only used by string discovery fields
        async for val, count in values_with_counts
        if censor_count(count, threshold)
    ]

    # Ensure options have a consistent sort order. For now, sort alphabetically, but in the future we may wish to sort
    # by count or something like that. PyCharm gets angry about passing str.casefold directly, but it works fine.
    # noinspection PyTypeChecker
    res.sort(key=str.casefold)

    return res


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


async def get_age_numeric_binned(
    individual_queryset: QuerySet,
    bin_size: int,
    discovery: DiscoveryConfig,
    field_permissions: DataPermissions,
) -> dict:
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
        b: thresholded_count(bv, discovery, field_permissions)
        for b, bv in individuals_age.items()
    }


async def get_month_date_range(
    queryset_entity: DiscoveryEntity, queryset: QuerySet, field_props: DateFieldDefinition, threshold: int
) -> tuple[str | None, str | None]:
    """
    Get start date and end date from the database
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Aggregate functions
     are not available for data in JSON fields.
    Implement handling dates as regular fields when needed.
    TODO: for now only dates binned by month are handled.
    """

    # As mentioned above, currently only bin_by=month is supported. This is validated by the Pydantic model, so we don't
    # need to check for it here.

    field_name = f_utils.get_field_django_mapping(queryset_entity, field_props)

    if "extra_properties" not in field_name:
        raise NotImplementedError("Binning date-like fields that are not in extra_properties is not implemented")

    is_not_null_filter = {f"{field_name}__isnull": False}   # property may be missing: avoid handling "None"

    # Note: lexicographic sort is correct with date strings like `2021-03-09`
    # TODO: this can leak months that have below threshold count!
    # TODO: should this be passed a queryset?
    query_set = (
        queryset
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


async def get_range_stats(
    scope: ValidatedDiscoveryScope,
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    field_props: NumberFieldDefinition,
    field_permissions: DataPermissions,
) -> BinList:
    field_mapping = f_utils.get_field_django_mapping(queryset_entity, field_props)

    # JSONField array specific field props
    group_by = getattr(field_props, "group_by", None)
    group_by_value = getattr(field_props, "group_by_value", None)
    value_mapping = getattr(field_props, "value_mapping", None)

    # Generate a list of When conditions that return a label for the given bin.
    # This is equivalent to an SQL CASE statement.
    if group_by and group_by_value and value_mapping:
        # group_by, group_by_value and value_mapping are required field props to get range stats on a JSONField array.
        whens = [When(
            # Django's gte and lte lookups cannot span multiple JSON array indexes,
            # so we use the jsonb_path_exists function instead.
            f_utils.get_json_range_condition(queryset_entity, field_props, min_value=floor, max_value=ceil),
            then=Value(label)
        ) for floor, ceil, label in f_utils.labelled_range_generator(field_props)]
    else:
        whens = [
            When(
                **{f"{field_mapping}__gte": floor} if floor is not None else {},
                **{f"{field_mapping}__lt": ceil} if ceil is not None else {},
                then=Value(label),
            )
            for floor, ceil, label in f_utils.labelled_range_generator(field_props)
        ]

    queryset = (
        queryset
        .values(label=Case(*whens, default=Value("missing"), output_field=CharField()))
        .annotate(total=Count("label"))
    )

    # Maximum number of entries needed to round a count from its true value down to 0 (censored discovery)
    stats: dict[str, int] = dict()
    async for item in queryset:
        stats[item["label"]] = thresholded_count(item["total"], scope, field_permissions)

    # All the bins between start and end must be represented and ordered
    bins: BinList = BinList(root=[
        BinWithValue(label=label, value=stats.get(label, 0))
        for floor, ceil, label in f_utils.labelled_range_generator(field_props)
    ])

    if "missing" in stats:
        bins.append(BinWithValue(label="missing", value=stats["missing"]))

    return bins


async def get_categorical_stats(
    scope: ValidatedDiscoveryScope,
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    field_props: StringFieldDefinition,
    field_permissions: DataPermissions,
) -> BinList:
    """
    Fetches statistics for a given categorical field and apply privacy policies
    """
    field_name = f_utils.get_field_django_mapping(queryset_entity, field_props)

    # Collect stats for the field, censoring low cell counts along the way
    # - We cannot append 0-counts for derived labels, since that indicates there is a non-0 count for this label in the
    #   database - i.e., if the label is pulled from the values in the database, someone could otherwise learn
    #   1 <= this field <= threshold given it being present at all.
    # - stats_for_field(...) handles this!
    stats: Mapping[str, int] = await stats_for_field(
        queryset, scope.discovery, field_name, field_permissions, add_missing=True, group_by=field_props.group_by
    )

    # Enforce values order from config and apply policies
    labels: list[str] | None = getattr(field_props.config, "enum")
    derived_labels: bool = labels is None

    # Special case: for some fields, values are based on what's present in the
    # dataset (enum is null in the public JSON).
    # - Here, apply lexical sort, and exclude the "missing" value which will
    #   be appended at the end if it is set.
    # - Note that in this situation, we explictly MUST HAVE remove rounded-down 0-counts (below the threshold) below,
    #   otherwise we LEAK that there is 1 <= x <= threshold matching entries in the DB. However, since
    #   stats_for_field(...) has already handled not adding these keys, these labels don't make it into this list.
    if derived_labels:
        labels = sorted(
            [k for k in stats.keys() if k != "missing"],
            key=lambda x: x.lower()
        )

    # Create bin structures for each label, and add an extra `missing` bin for items missing a value for this field.
    return BinList(root=[
        # Don't need to re-censor counts - we've already censored them in stats_for_field(...):
        *(BinWithValue(label=category, value=stats.get(category, 0)) for category in labels),
        BinWithValue(label="missing", value=stats["missing"]),
    ])


async def get_date_stats(
    scope: ValidatedDiscoveryScope,
    queryset_entity: DiscoveryEntity,
    queryset: QuerySet,
    field_props: DateFieldDefinition,
    field_permissions: DataPermissions,
) -> BinList:
    """
    Fetches statistics for a given date field, fill the gaps in the date range
    and apply privacy policies.
    Note that dates within a JSON are stored as strings, not instances of datetime.
    TODO: for now, only dates in extra_properties are handled. Handle dates as
     regular fields when needed.
    TODO: for now only dates binned by month are handled
    """

    # As mentioned above, currently only bin_by=month is supported. This is validated by the Pydantic model, so we don't
    # need to check for it here.

    field_name = f_utils.get_field_django_mapping(queryset_entity, field_props)

    if "extra_properties" not in field_name:
        msg = "Binning date-like fields that are not in extra-properties is not implemented"
        raise NotImplementedError(msg)

    # Note: lexical sort works on ISO dates
    queryset = (
        queryset
        .values(field_name)
        .order_by(field_name)
        .annotate(total=Count(field_name))
    )

    stats = defaultdict(int)
    start: str | None = None
    end: str | None = None
    # Key the counts on yyyy-mm combination (aggregate same month counts)
    async for item in queryset:
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
    bins: BinList = BinList(root=[])
    if start:   # at least one month
        for year, month in f_utils.monthly_generator(start, end or start):
            key = f"{year}-{month:02d}"
            label = f"{month_abbr[month].capitalize()} {year}"    # convert key as yyyy-mm to `abbreviated month yyyy`
            bins.append(BinWithValue(
                label=label,
                value=thresholded_count(stats.get(key, 0), scope.discovery, field_permissions),
            ))

    # Append missing items at the end if any
    if "missing" in stats:
        bins.append(BinWithValue(
            label="missing",
            value=thresholded_count(stats["missing"], scope.discovery, field_permissions),
        ))

    return bins


def get_condition_for_non_jsonb_field(
    field: str,
    ops: tuple[tuple[str, int | str], ...],
    subquery: DiscoveryFieldSubquery | None,
):
    if subquery:
        # If we do a simple filter on `field` in the case of crossing a many-to-many or many-to-one
        # relationship boundary, we end up with an inner join that prevents us from getting correct stats of
        # values for the matching queryset entity.
        # Instead, we do an Exists subquery to check if we have at least one matching object from the other side
        # of the m2m/many-to-one relation which matches the field query (which as been rewritten to be valid for
        # the model referred to in the relation rather than the queryset model.)
        return Q(Exists(
            subquery.queryset.filter(**{
                subquery.related_field: OuterRef("pk"),
                **{f"{subquery.inner_field}__{op}": value for op, value in ops}
            })
        ))
    else:
        return Q(**{f"{field}__{op}": value for op, value in ops})


def symbol_django_op(sym: str) -> str:
    match sym:
        case "<" | ")":
            return "lt"
        case "≤" | "]":
            return "lte"
        case ">" | "(":
            return "gt"
        case "≥" | "[":
            return "gte"
        case _:
            raise NotImplementedError()


async def filter_queryset_field_value(
    queryset_entity: DiscoveryEntity, qs: QuerySet, field_props: FieldDefinition, value: str, logger: BoundLogger
) -> tuple[QuerySet, DiscoveryEntity]:
    """
    Further filter a queryset using the field defined by field_props and the
    given value.
    It is a prerequisite that the field mapping defined in field_props is represented
    in the queryset object.
    `mapping_for_search_filter` is an optional property that gets precedence over `mapping`
    for the necessity of filtering. It is not necessary to specify this when
    the `mapping` value is based on the same model as the queryset.
    """

    # - can throw DiscoveryFilterRewriteException if we cannot rewrite the field mapping as a subpath of the queryset
    #   model
    field, subquery, queried_entity = get_field_django_mapping_and_queried_entity(queryset_entity, field_props)

    # TODO: resolve schema including extra properties

    if field_props.datatype in ("string", "ontology_class"):
        if gb := field_props.group_by:
            if field_props.datatype == "ontology-class":
                # append `/id` to path to search by ontology class ID
                gb = gb + "/id"

            # JSONField array string check must use 'contains' lookup
            nested_condition = f_utils.get_nested_json_condition(gb, value)
            condition = Q(**{f"{field}__contains": [nested_condition]})
        else:
            f = field
            if field_props.datatype == "ontology-class":
                # append __id to path to search by ontology class ID
                f += "__id"
            condition = get_condition_for_non_jsonb_field(f, (("iexact", value),), subquery)

    elif field_props.datatype == "number":
        # values are of the form "[50, 150)", "< 50" or "≥ 800".
        # important: custom bins can have decimals in them!

        if mrp_match := MIDDLE_RANGE_PATTERN.match(value):
            # full value looks like "[50, 60)", "< 50", or "≥ 60" if we're validating bins line up with censored
            # discovery (validated elsewhere).
            # with full discovery access (query:data), we can accept the following other forms:
            #   "(50, 60)", "[50, 60)", "[50, 60]", "≥50, <60", "≤ 50", "> 60"

            start_op = symbol_django_op(mrp_match["start_sym"])
            end_op = symbol_django_op(mrp_match["end_sym"])
            start = f_utils.str_to_numeric(mrp_match["start"])
            end = f_utils.str_to_numeric(mrp_match["end"])

            if json_range_condition := f_utils.get_json_range_condition(
                queryset_entity,
                field_props,
                min_value=start,
                min_inclusive=start_op == "gte",
                max_value=end,
                max_inclusive=end_op == "lte",
            ):
                # JSONField array range stats must use 'jsonb_path_exists' conditions
                condition = json_range_condition
            else:
                condition = get_condition_for_non_jsonb_field(field, ((start_op, start), (end_op, end)), subquery)

        elif brp_match := BEGIN_RANGE_PATTERN.match(value):
            # full value looks like "> 50" or "≥ 50" (only the latter is valid for censored discovery.)
            val = f_utils.str_to_numeric(brp_match["val"])
            min_op = symbol_django_op(brp_match["sym"])
            if json_range_condition := f_utils.get_json_range_condition(
                queryset_entity, field_props, min_value=val, min_inclusive=min_op == "gte"
            ):
                condition = json_range_condition
            else:
                condition = get_condition_for_non_jsonb_field(field, ((min_op, val),), subquery)

        elif erp_match := END_RANGE_PATTERN.match(value):
            # full value looks like "< 50" or "≤ 50" (only the former is valid for censored discovery.)
            val = f_utils.str_to_numeric(erp_match["val"])
            max_op = symbol_django_op(erp_match["sym"])
            if json_range_condition := f_utils.get_json_range_condition(
                queryset_entity, field_props, max_value=val, max_inclusive=max_op == "lte"
            ):
                condition = json_range_condition
            else:
                condition = get_condition_for_non_jsonb_field(field, ((max_op, val),), subquery)

        else:
            raise NotImplementedError()

    elif field_props.datatype == "date":
        # For now, limited to date expressed as month/year such as "May 2022"
        d = datetime.datetime.strptime(value, "%b %Y")
        val = d.strftime("%Y-%m")   # convert to "yyyy-mm" format to search for dates as "2022-05-03"
        condition = get_condition_for_non_jsonb_field(field, (("startswith", val),), subquery)

    else:  # pragma: no cover
        # This isn't possible to reach by normal means, since the FieldDefinition Pydantic model limits the possible
        # values of `datatype` to the cases above (unless a new possible value is added to FieldDefinition).
        raise NotImplementedError()

    await logger.adebug(
        "filtering entity field with condition", entity=queried_entity, field=field, condition=condition
    )

    return qs.filter(condition), queried_entity
