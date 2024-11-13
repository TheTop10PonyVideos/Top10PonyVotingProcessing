"""Functions for parsing the calculated top 10 spreadsheet so that we can
perform post-processing procedures using its data.

The calculated top 10 CSV looks something like this:

    Title,Uploader,Percentage,Total Votes,URL,Notes
    Example 1,Uploader 1,90.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 2,Uploader 2,80.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 3,Uploader 3,70.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 4,Uploader 4,60.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 5,Uploader 5,50.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 6,Uploader 6,40.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 7,Uploader 7,30.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 8,Uploader 8,20.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 9,Uploader 9,10.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    Example 10,Uploader 10,5.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    ,,,,,
    HONORABLE MENTIONS,,,,,
    ,,,,,
    Example 11,Uploader 11,4.0000%,20,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    ...
    ,,,,,
    HISTORY,,,,,
    ,,,,,
    1 year ago,,,,,
    ,,,,,
    Misclick - A Fallout Equestria Animation,,,,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    ...
    ,,,,,
    5 years ago,,,,,
    ,,,,,
    Just relax and read [Animation],,,,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    ...
    ,,,,,
    10 years ago,,,,,
    ,,,,,
    Princess Celestia Being Deep (Old),,,,https://www.youtube.com/watch?v=dmVWvOC_2HU,
    ...


Due to the lack of formatting options in a CSV file, some "records" are actually
headings included for human readability, and aren't part of the data; instead,
they serve the structural purpose of categorizing the records. There are 3
categories:

* The top 10 videos
* HONORABLE MENTIONS: Videos from that month which didn't make the top 10, but
  were still recognized
* HISTORY: Lists of videos from past Top 10 Pony Videos showcases, further
  categorized by anniversary year
"""


def group_records_by_headings(
    records: list,
    headings: list,
    heading_field: str,
    empty_heading: str = "(NO HEADING)",
) -> dict:
    """Given an ordered list of records, some of which are acting as headings,
    split the records into the groups delimited by each heading.

    A record acting as a heading is expected to use a specific field to contain
    the heading value; this must be specified as an argument."""

    grouped_records = {}
    curr_heading = empty_heading

    # Scan record-by-record until a heading is found.
    for record in records:
        cand_heading = record[heading_field]
        if cand_heading in headings:
            curr_heading = cand_heading

            if curr_heading in grouped_records:
                raise ValueError(
                    f'Cannot group records by headings; the heading "{curr_heading}" is not unique'
                )

            grouped_records[curr_heading] = []
            continue

        if curr_heading not in grouped_records and curr_heading == empty_heading:
            grouped_records[curr_heading] = []

        grouped_records[curr_heading].append(record)

    return grouped_records


def parse_calculated_top_10_csv(records: list[dict]) -> dict:
    """Given a list of row records from a calculated top 10 CSV file, parse the
    file into a collection of records grouped by category."""

    # Remove empty row records (these are only included for readability)
    records = [
        record
        for record in records
        if "".join([record[k] for k in record]).strip() != ""
    ]

    # Group the records by heading. (The "Top 10" heading is the implicit empty
    # heading).
    headings = ["HONORABLE MENTIONS", "HISTORY"]
    grouped_records = group_records_by_headings(records, headings, "Title", "Top 10")

    # For the history records, further group them by anniversary name.
    is_anni_record = lambda r: " year ago" in r["Title"] or " years ago" in r["Title"]
    anni_names = [r["Title"] for r in grouped_records["HISTORY"] if is_anni_record(r)]

    grouped_hist_records = group_records_by_headings(
        grouped_records["HISTORY"], anni_names, "Title"
    )
    grouped_records["HISTORY"] = grouped_hist_records

    return grouped_records
