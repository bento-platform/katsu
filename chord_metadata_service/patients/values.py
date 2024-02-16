from abc import ABC


__all__ = [
    "Sex",
    "KaryotypicSex",
    "PatientStatus",
]


class ValuesCollection(ABC):
    values: tuple[str, ...] = ()

    @classmethod
    def as_django_values(cls):
        return tuple((x, x) for x in cls.values)

    @classmethod
    def as_list(cls):
        return list(cls.values)


class Sex(ValuesCollection):
    UNKNOWN_SEX = "UNKNOWN_SEX"
    FEMALE = "FEMALE"
    MALE = "MALE"
    OTHER_SEX = "OTHER_SEX"
    values = (
        UNKNOWN_SEX,
        FEMALE,
        MALE,
        OTHER_SEX,
    )


class KaryotypicSex(ValuesCollection):
    UNKNOWN_KARYOTYPE = "UNKNOWN_KARYOTYPE"
    XX = "XX"
    XY = "XY"
    XO = "XO"
    XXY = "XXY"
    XXX = "XXX"
    XXYY = "XXYY"
    XXXY = "XXXY"
    XXXX = "XXXX"
    XYY = "XYY"
    OTHER_KARYOTYPE = "OTHER_KARYOTYPE"
    values = (
        UNKNOWN_KARYOTYPE,
        XX,
        XY,
        XO,
        XXY,
        XXX,
        XXYY,
        XXXY,
        XXXX,
        XYY,
        OTHER_KARYOTYPE,
    )


class PatientStatus(ValuesCollection):
    UNKNOWN_STATUS = "UNKNOWN_STATUS"
    ALIVE = "ALIVE"
    DECEASED = "DECEASED"
    values = (
        UNKNOWN_STATUS,
        ALIVE,
        DECEASED
    )
