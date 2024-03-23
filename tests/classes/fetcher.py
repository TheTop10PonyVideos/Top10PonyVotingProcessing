from unittest import TestCase
from classes.fetcher import Fetcher
from classes.exceptions import FetchRequestError, FetchParseError, UnsupportedHostError


class TestFetcher(TestCase):
    def test_fetch(self):
        # Test fetch with no fetch services defined
        fetcher = Fetcher()

        with self.assertRaises(UnsupportedHostError):
            fetcher.fetch('https://example.com')

        # Test fetch with incorrectly-defined fetch services
        class InvalidMockFetchService:
            pass

        fetcher = Fetcher()
        service = InvalidMockFetchService()

        with self.assertRaises(NotImplementedError):
            fetcher.add_service('invalid_mock', service)

        # Test fetch with no capable services
        class IncapableMockFetchService:
            def can_fetch(self, url):
                return False

            def request(self, url):
                pass

            def parse(self, response):
                pass

        fetcher = Fetcher()
        service = IncapableMockFetchService()
        fetcher.add_service('incapable_mock', service)

        with self.assertRaises(UnsupportedHostError):
            fetcher.fetch('https://example.com')

        # Test fetch with service that returns an error
        class FailureMockFetchService:
            def can_fetch(self, url):
                return True

            def request(self, url):
                raise FetchRequestError('Request failed')

            def parse(self, response):
                pass

        fetcher = Fetcher()
        service = FailureMockFetchService()
        fetcher.add_service('failure_mock', service)

        with self.assertRaises(FetchRequestError):
            fetcher.fetch('https://example.com')

        # Test fetch with service that successfully returns data, but fails to
        # parse it
        class ParseFailureMockFetchService:
            def can_fetch(self, url):
                return True

            def request(self, url):
                return {'title': 'Example video'}

            def parse(self, response):
                raise FetchParseError('Parsing failed')

        fetcher = Fetcher()
        service = ParseFailureMockFetchService()
        fetcher.add_service('parse_failure_mock', service)

        with self.assertRaises(FetchParseError):
            fetcher.fetch('https://example.com')

        # Test fetch with service that successfully and parses data
        class SuccessMockFetchService:
            def can_fetch(self, url):
                return True

            def request(self, url):
                return {'title': 'Example Video'}

            def parse(self, response):
                return {'title': response['title']}

        fetcher = Fetcher()
        service = SuccessMockFetchService()
        fetcher.add_service('success_mock', service)
        video_data = fetcher.fetch('https://example.com')
        self.assertEqual('Example Video', video_data['title'])
