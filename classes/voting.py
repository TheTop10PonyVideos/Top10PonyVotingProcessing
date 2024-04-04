from datetime import datetime


class Annotations:
    """Class representing a collection of annotations, with methods to add,
    query, and render annotation labels."""

    def __init__(self):
        self.annotations: list[str] = []

    def add(self, annotation: str):
        """Add an annotation."""
        self.annotations.append(annotation)

    def has(self, annotation: str) -> bool:
        """Return True if the given annotation exists."""
        return annotation in self.annotations

    def count(self) -> int:
        """Return the number of annotations."""
        return len(self.annotations)

    def has_none(self) -> bool:
        """Return True if no annotations exist."""
        return self.count() == 0

    def get_label(self, left_enclosure: str = "[", right_enclosure: str = "]") -> str:
        """Return a string consisting of all the annotations surrounded by
        enclosing characters and concatenated together, or None if no
        annotations exist. This allows for more convenient and readable output.
        """
        if len(self.annotations) == 0:
            return None

        return "".join(
            [
                f"{left_enclosure}{annotation}{right_enclosure}"
                for annotation in self.annotations
            ]
        )


class Vote:
    """Class representing a vote, with optional annotations."""

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.annotations = Annotations()


class Video:
    """Class representing a video and its metadata, with optional annotations."""

    def __init__(self, data: dict = None):
        super().__init__()
        self.data = data
        self.annotations = Annotations()

    def __getitem__(self, key):
        """For ease of data access, delegate subscript indexing to `data`
        dictionary.
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """Delegate subscript assignment to `data` dictionary."""
        self.data[key] = value
        return self.data[key]

    def __contains__(self, key):
        """Delegate `in` operation to `data` dictionary."""
        return key in self.data


class Ballot:
    """Class representing a set of votes from one person, along with the
    timestamp of their submission.
    """

    def __init__(self, timestamp: datetime, votes: list[Vote]):
        self.timestamp = timestamp
        self.votes = votes
