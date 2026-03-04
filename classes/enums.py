from enum import Enum


class VideoState(Enum):
    """Represents a problematic state that a video on the master archive can be shown to have"""
                    # TODO: correct LS
    NON_EMBEDDABLE = ("non-embedable", "non-embeddable")
    UNAVAILABLE = ("unavailable", "deleted", "private", "tos deleted", "terminated")
    AGE_RESTRICTED = ("age-restricted",)
    BLOCKED = ("blocked",)

    @classmethod
    def get(cls, value: str):
        for state in cls:
            if value.lower() in state.value:
                return state


class CSVType(Enum):
    """Represents the kind of CSV file being used as an input"""
    MASTER_ARCHIVE = "Master Archive"
    HONORABLE_MENTIONS = "Honorable Mentions"
    GENERIC_LIST = "Generic List"
