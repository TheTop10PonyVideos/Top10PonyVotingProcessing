"""Small collection of functions for performing similarity checks."""

from fuzzywuzzy import fuzz
from functions.url import is_youtube_url, normalize_youtube_url
from classes.voting import Video


def get_string_similarity(string_a: str, string_b: str) -> float:
    """Return the similarity between two strings as a number between 0 and 100."""
    return fuzz.ratio(string_a, string_b)


def get_duration_similarity(
    duration_a: float, duration_b: float, threshold: float = 5
) -> float:
    """Return the similarity between two durations (given in seconds) as a
    number between 0 and 100. Two durations are considered 100% similar if they
    are exactly the same, 0% similar if they are more than 5 seconds apart, and
    otherwise some value in between.

    Examples:
        # similarity = 100 as they are the same duration
        get_duration_similarity(96, 96)

        # similarity = 0 as they are more than 5 seconds apart
        get_duration_similarity(96, 90)

        # similarity = 50 as they are exactly 2.5 seconds apart
        get_duration_similarity(96, 98.5)

    5 seconds is the default threshold, but this can be changed via the
    threshold argument."""

    difference = abs(duration_b - duration_a)
    difference = min(difference, threshold)
    percent_diff = (difference / threshold) * 100
    percent_similarity = 100 - percent_diff

    return percent_similarity


def get_similarity_matrix(table: dict[str], similarity_func) -> list[list[float]]:
    """Given a dictionary representing a table of key-value pairs, return a 2D
    matrix in which each row corresponds to a URL, and contains a list of
    numbers from 0 to 100 which represent its similarity to each URL in the
    table. The URLs are indexed by their lexicographic ordering. Similarity is
    determined by the given similarity function."""
    similarity_matrix = []

    ordered_keys = sorted(table)
    for j, key_j in enumerate(ordered_keys):
        row = []
        value_j = table[key_j]
        for i, key_i in enumerate(ordered_keys):
            value_i = table[key_i]
            similarity = similarity_func(value_j, value_i)
            row.append(similarity)

        similarity_matrix.append(row)

    return similarity_matrix


def detect_cross_platform_uploads(videos: dict[str, Video]) -> dict[str, list[str]]:
    """Given a dictionary mapping video URLs to Video objects, analyze each
    video for its similarity to other videos in the collection, and produce a
    similarity table, which maps URLs to subtables of the videos they are
    similar to.

    The subtables are also tables of URLs, each one mapped to a list of
    properties in which the two URLs are similar.

    The properties that are checked for similarity are `title`, `uploader`, and
    `duration`.

    To prevent false positives, video URLs are normalized first, and all minor
    variants of the same URL are combined into a single canonical URL. This
    means that the URLs in the output similarity table may not precisely match
    the URLs that were in the input dictionary.

    As a further refinement step, similarities are only considered if multiple
    properties flag as similar - specifically:

    * similar title, uploader, and duration
    * similar title and uploader
    * similar title and duration
    """

    properties = ["title", "uploader", "duration"]
    string_similarity_threshold = 90

    videos_with_data = {
        url: video for url, video in videos.items() if video.data is not None
    }

    # Normalization step: The videos list may contain many variants of the same
    # URL - usually YouTube URLs with varying parameter orderings. For the
    # purpose of cross-platform comparisons, it's easier if we eliminate all
    # these variants and just have a single canonical URL for a given site.
    videos_with_data = {
        normalize_youtube_url(url) if is_youtube_url(url) else url: video
        for url, video in videos_with_data.items()
    }

    # For each property we're interested in, get a table mapping each URL to its
    # value for that property.
    prop_tables = {}
    for prop in properties:
        prop_tables[prop] = {
            url: video.data[prop] for url, video in videos_with_data.items()
        }

    # Use the property tables to get a similarity matrix for each property.
    similarity_matrices = {
        "title": get_similarity_matrix(prop_tables["title"], get_string_similarity),
        "uploader": get_similarity_matrix(
            prop_tables["uploader"], get_string_similarity
        ),
        "duration": get_similarity_matrix(
            prop_tables["duration"], get_duration_similarity
        ),
    }

    # Using the similarity matrices, build a table which maps video URLs to a
    # subtable of the URLs it is similar to. The subtable contains a list of the
    # properties in which the two videos are similar.
    similarity_table = {}

    ordered_urls = sorted(videos_with_data)
    for prop, similarity_matrix in similarity_matrices.items():
        # Use a threshold of 0 for duration similarities, as anything within
        # 5 seconds has a non-zero similarity.
        similarity_threshold = 0 if prop == "duration" else string_similarity_threshold

        for j, row in enumerate(similarity_matrix):
            # Use the row index to look up the URL being compared
            video_url = ordered_urls[j]

            if video_url not in similarity_table:
                similarity_table[video_url] = {}

            # Get the indices of all URLs that pass the similarity threshold.
            similarity_indices = [
                i
                for i, similarity in enumerate(row)
                if similarity > similarity_threshold
            ]

            # Use the gathered indices to look up the URLs (ignoring the one
            # that's the same as the URL being compared, as we're not interested
            # in self-similarity).
            similarity_urls = [
                ordered_urls[si]
                for si in similarity_indices
                if ordered_urls[si] != video_url
            ]

            # For each of the URLs that passed the similarity threshold, add
            # them to the similarity table against the URL being compared, and
            # add the property for which they are similar.
            for similarity_url in similarity_urls:
                if similarity_url not in similarity_table[video_url]:
                    similarity_table[video_url][similarity_url] = []
                similarity_table[video_url][similarity_url].append(prop)

    # Filter out any property combinations we're not interested in.
    allowed_prop_combos = [
        ["title", "uploader", "duration"],
        ["title", "uploader"],
        ["title", "duration"],
    ]

    for url, subtable in similarity_table.items():
        similarity_table[url] = {
            u: props for u, props in subtable.items() if props in allowed_prop_combos
        }

    # Remove any empty entries from the similarity table (ie. videos that were
    # not similar to any others)
    similarity_table = {
        url: subtable for url, subtable in similarity_table.items() if len(subtable) > 0
    }

    return similarity_table
