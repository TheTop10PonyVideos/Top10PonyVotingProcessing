"""Rule checks for ballots."""

from pathlib import Path
from fuzzywuzzy import fuzz
from classes.voting import Ballot, Vote, Video


def check_duplicates(ballots: list[Ballot]):
    """For each listed ballot, check its vote values and annotate those which
    are duplicates of earlier votes in the list.
    """
    for ballot in ballots:
        unique_votes = []
        for vote in ballot.votes:
            if vote.url in unique_votes:
                vote.annotations.add("DUPLICATE VIDEO")
            else:
                unique_votes.append(vote.url)


def check_blacklisted_ballots(ballots: list[Ballot], videos: dict[str, Video]):
    """Given a list of ballots and a dictionary of annotated videos indexed by
    URL, annotate any votes for videos which have been marked as blacklisted.
    """
    for ballot in ballots:
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.annotations.has("BLACKLISTED"):
                vote.annotations.add("BLACKLISTED")


def check_ballot_upload_dates(ballots: list[Ballot], videos: dict[str, Video]):
    """Given a list of ballots and a dictionary of annotated videos indexed by
    URL, annotate any votes for videos which have an invalid upload date.
    """
    for ballot in ballots:
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.annotations.has("VIDEO TOO OLD"):
                vote.annotations.add("VIDEO TOO OLD")
            if video.annotations.has("VIDEO TOO NEW"):
                vote.annotations.add("VIDEO TOO NEW")


def check_ballot_video_durations(ballots: list[Ballot], videos: dict[str, Video]):
    """Given a list of ballots and a dictionary of annotated videos indexed by
    URL, annotate any votes for videos which have an invalid duration.
    """
    for ballot in ballots:
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.annotations.has("VIDEO TOO SHORT"):
                vote.annotations.add("VIDEO TOO SHORT")
            if video.annotations.has("VIDEO MAYBE TOO SHORT"):
                vote.annotations.add("VIDEO MAYBE TOO SHORT")


def check_fuzzy(
    ballots: list[Ballot], videos: dict[str, Video], similarity_threshold: float
):
    """Given a list of ballots, check each vote in the ballot to see if it is
    similar to other votes in the same ballot for each of 3 properties: title,
    uploader, and duration. For each vote that is found to be similar to others,
    annotate it with the properties in which it is similar.
    """
    for ballot in ballots:
        # TODO: Why are we doing Levenshtein check on duration? Does it even
        # work on numbers?
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
            unchecked_votes = set([vote for vote in ballot.votes])
            while len(unchecked_votes) > 0:
                vote_to_check = unchecked_votes.pop()
                video_to_check = videos[vote_to_check.url]

                if video_to_check.data is None:
                    continue

                prop_to_check = video_to_check.data[property_name]

                # TODO: This string conversion is here because for some reason
                # we're comparing durations (integer values) with the fuzzy
                # check, which I don't think is useful.
                prop_to_check = str(prop_to_check)

                is_similar = lambda a, b: fuzz.ratio(a, b) >= similarity_threshold
                similar_votes = set(
                    [
                        vote
                        for vote in unchecked_votes
                        if (video_data := videos[vote.url].data) is not None
                        and is_similar(prop_to_check, str(video_data[property_name]))
                    ]
                )

                if len(similar_votes) > 0:
                    similarity_sets[property_name].add(vote_to_check)
                    similarity_sets[property_name].update(similar_votes)

        property_order = ["title", "uploader", "duration"]

        for vote in ballot.votes:
            vote_similarity_properties = [
                prop for prop in property_order if vote in similarity_sets[prop]
            ]

            if len(vote_similarity_properties) > 0:
                annotation = f"SIMILARITY DETECTED IN {' AND '.join([category.upper() for category in vote_similarity_properties])}"
                vote.annotations.add(annotation)


def check_ballot_uploader_occurrences(ballots: list[Ballot], videos: dict[str, Video]):
    """Given a list of ballots and a dictionary of videos indexed by URL,
    annotate any votes for videos whose uploader occurs too many times in the
    ballot.
    """
    for ballot in ballots:
        uploaders = []
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.data is not None:
                uploaders.append(video["uploader"])

        uploader_counts = {}
        for uploader in uploaders:
            uploader_counts[uploader] = uploader_counts.get(uploader, 0) + 1

        for vote in ballot.votes:
            video = videos[vote.url]
            if video.data is not None:
                if uploader_counts[video["uploader"]] >= 3:
                    vote.annotations.add("DUPLICATE CREATOR")


def check_ballot_uploader_diversity(ballots: list[Ballot], videos: dict[str, Video]):
    """Given a list of ballots and a dictionary of videos indexed by URL, if the
    ballot contains too few unique uploaders, annotate every vote in the ballot.
    """
    for ballot in ballots:
        uploaders = []
        for vote in ballot.votes:
            video = videos[vote.url]
            if video.data is not None:
                uploaders.append(video["uploader"])

        unique_uploaders = set(uploaders)

        if len(unique_uploaders) < 5:
            for vote in ballot.votes:
                vote.annotations.add("5 CHANNEL RULE")
