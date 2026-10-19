"""Rule checks for ballots."""

from fuzzywuzzy import fuzz
from classes.voting import Ballot
from pandas import DataFrame


def check_duplicates(ballots: list[Ballot]):
    """For each listed ballot, check its vote values and annotate those which
    are duplicates of earlier votes in the list.
    """
    for ballot in ballots:
        unique_votes = []
        for vote in ballot.nonempty_votes():
            if vote.url in unique_votes:
                vote.annotations.add("DUPLICATE VIDEO")
            else:
                unique_votes.append(vote.url)


def check_fuzzy(
    ballots: list[Ballot], videos: DataFrame, similarity_threshold: float
):
    """Given a list of ballots, check each vote in the ballot to see if it is
    similar to other votes in the same ballot for each of 3 properties: title,
    uploader, and duration. For each vote that is found to be similar to others,
    annotate it with the properties in which it is similar.
    """
    # TODO: Consider replacing this with the similarity matrix check.
    for ballot in ballots:
        # TODO: Is Levenshtein check on duration needed? I'm not sure it works
        # on numbers.
        similarity_sets = {
            "title": set(),
            "uploader": set(),
            "duration": set(),
        }

        # Set-based approach to similarity check:
        # * Pop a vote from the unchecked set
        # * Get the set of all unchecked votes similar to it
        # * Store that set, repeat until no more votes or no more similar sets
        for property_name, similarity_set in similarity_sets.items():
            unchecked_votes = set([vote for vote in ballot.nonempty_votes()])
            while len(unchecked_votes) > 0:
                vote_to_check = unchecked_votes.pop()
                video_to_check = videos.loc[vote_to_check.url]

                # Using title prescence to determine if there is video data
                if not video_to_check['title']:
                    continue

                prop_to_check = video_to_check[property_name]

                # TODO: This string conversion is here because for some reason
                # we're comparing durations (integer values) with the fuzzy
                # check. Possibly we may want to use a different check for this.
                prop_to_check = str(prop_to_check)

                is_similar = lambda a, b: fuzz.ratio(a, b) >= similarity_threshold
                similar_votes = set(
                    [
                        vote
                        for vote in unchecked_votes
                        if (video_data := videos.loc[vote.url])['title']
                        and is_similar(prop_to_check, str(video_data[property_name]))
                    ]
                )

                if len(similar_votes) > 0:
                    similarity_sets[property_name].add(vote_to_check)
                    similarity_sets[property_name].update(similar_votes)

        property_order = ["title", "uploader", "duration"]

        for vote in ballot.nonempty_votes():
            vote_similarity_properties = [
                prop for prop in property_order if vote in similarity_sets[prop]
            ]

            if len(vote_similarity_properties) > 0:
                annotation = f"SIMILARITY DETECTED IN {' AND '.join([category.upper() for category in vote_similarity_properties])}"
                vote.annotations.add(annotation)


def check_ballot_uploader_occurrences(ballots: list[Ballot], videos: DataFrame):
    """Given a list of ballots and a dictionary of videos indexed by URL,
    annotate any votes for videos whose uploader occurs too many times in the
    ballot.
    """
    for ballot in ballots:
        votes = ballot.nonempty_votes()

        uploader_counts = videos.loc[[vote.url for vote in votes], 'uploader'].value_counts()

        for vote in votes:
            uploader = videos.loc[vote.url, 'uploader']

            if uploader_counts[uploader] >= 3:
                vote.annotations.add("DUPLICATE CREATOR")
