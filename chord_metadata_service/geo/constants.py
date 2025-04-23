from pycountry import countries

__all__ = [
    "ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES",
    "ISO_3166_1_ALPHA_3_COUNTRY_CODES",
    "MODEL_ATTRS_TO_PREDEF_PROPS",
    "MODEL_PREDEF_PROPS_TO_ATTRS",
]

# noinspection PyUnresolvedReferences
ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES = {c.alpha_3: c.name for c in list(countries)}

# noinspection PyUnresolvedReferences
ISO_3166_1_ALPHA_3_COUNTRY_CODES = list(ISO_3166_1_ALPHA_3_COUNTRY_CODE_CHOICES.keys())

MODEL_ATTRS_TO_PREDEF_PROPS = {
    "label": "label",
    "city": "city",
    "country": "country",
    "iso_a3_code": "ISO3166alpha3",
    "precision": "precision",
}

MODEL_PREDEF_PROPS_TO_ATTRS = {v: k for k, v in MODEL_ATTRS_TO_PREDEF_PROPS.items()}
