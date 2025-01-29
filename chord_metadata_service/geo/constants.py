from pycountry import countries

__all__ = [
    "ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES",
    "ISO_3166_1_ALPHA_3_COUNTRY_CODES",
]

# noinspection PyUnresolvedReferences
ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES = {c.alpha_3: c.name for c in list(countries)}

# noinspection PyUnresolvedReferences
ISO_3166_1_ALPHA_3_COUNTRY_CODES = list(ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES.keys())
