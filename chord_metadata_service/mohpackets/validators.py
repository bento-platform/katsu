from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    RegexValidator,
)

# ID format.
# Examples: 90234, BLD_donor_89, AML-90
ID_VALIDATOR = RegexValidator(
    regex=r"^[A-Za-z0-9\-\._]{1,64}",
    message=_("The value does not fit the pattern [A-Za-z0-9\-\._]{1,64}"), # noqa
    code="invalid",
)

# Date format.
# A date, or partial date (e.g. just year or year + month) as used in
# human communication. The format is YYYY, YYYY-MM, or YYYY-MM-DD,
# e.g. 2018, 1973-06, or 1905-08-23. There SHALL be no time zone.
DATE_VALIDATOR = RegexValidator(
    regex=r"^([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1]))?)?",
    message=_("The value does not fit the pattern YYYY, YYYY-MM, or YYYY-MM-DD"),
    code="invalid",
)

# ICD-O-3 topography codes
# Examples: C50.1, C18
TOPOGRAPHY_VALIDATOR = RegexValidator(
    regex=r"^[8,9]{1}[0-9]{3}/[0,1,2,3,6,9]{1}[1-9]{0,1}$",
    message=_(
        "The value does not fit the pattern [8,9]{1}[0-9]{3}/[0,1,2,3,6,9]{1}[1-9]{0,1}"
    ),
    code="invalid",
)
