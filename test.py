# Unit test runner
#
# We're in the process of deprecating this test runner script in favor of
# pytest, which automatically discovers tests if the script filename begins with
# test_. Once all tests are renamed to begin with test_, this runner script can
# be deleted.
#
# pytest can still run unittest tests, so the tests themselves don't need to be
# rewritten.

import unittest
from tests.classes.fetcher import TestFetcher
from tests.classes.fetch_services import TestFetchServices
from tests.functions.general import TestFunctionsGeneral
from tests.functions.voting import TestFunctionsVoting
from tests.functions.date import TestFunctionsDate
from tests.functions.video_rules import TestFunctionsVideoRules
from tests.functions.ballot_rules import TestFunctionsBallotRules
from tests.functions.post_processing import TestFunctionsPostProcessing
from tests.functions.similarity import TestFunctionsSimilarity
from tests.functions.top_10_calc import TestFunctionsTop10Calc
from tests.functions.top_10_parser import TestFunctionsTop10Parser

# Run tests
unittest.main()
