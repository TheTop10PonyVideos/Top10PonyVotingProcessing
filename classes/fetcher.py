from classes.exceptions import UnsupportedHostError, FetchRequestError
from functions.manual_input import resolve


class Fetcher:
    """Video data fetcher class. Designed to be extensible and configurable at
    runtime. To configure the fetcher, use `add_service` to register
    `FetchService` objects; the fetcher will then use these to handle fetch
    requests.
    """

    def __init__(self, ensure_complete_data = False):
        self.services = {}
        self.cache = None
        self.printer = None
        self.ensure_complete_data = ensure_complete_data

    def add_service(self, name: str, fetch_service):
        """Add a fetch service to the fetcher."""

        required_methods = ["can_fetch", "request", "parse"]
        missing_methods = [
            method for method in required_methods if not hasattr(fetch_service, method)
        ]
        if len(missing_methods) > 0:
            raise NotImplementedError(
                f'Cannot add fetch service "{name}" to video data fetcher; fetch services must define the methods {", ".join(required_methods)}'
            )
        self.services[name] = fetch_service

    def get_capable_services(self, url: str) -> dict:
        """Return a dictionary of services that are capable of fetching data for
        the given URL.
        """
        return {
            name: service
            for name, service in self.services.items()
            if service.can_fetch(url)
        }

    def fetch(self, url: str) -> dict:
        """Multi-service fetch. `url` can be a URL for any service recognized by
        the fetcher. The fetcher will first query its services to find out which
        one is capable of handling the URL, then attempt to fetch video data
        using that service.

        If the fetcher has no services capable of handling the URL, an
        UnsupportedHostError is raised.

        If multiple services are capable of fetching the same URL, the first
        service found is used.
        """

        # Service check: check each registered service to see which can handle
        # the URL.
        capable_services = self.get_capable_services(url)
        if len(capable_services) == 0:
            raise UnsupportedHostError(
                f'Cannot fetch data for URL "{url}"; no services are capable of handling this URL'
            )

        service_name = [name for name in capable_services][0]
        service = capable_services[service_name]
        video_data = None

        # Cache check: If using a cache, and the video data for this service
        # and URL is already cached, skip the request phase.
        cache_key = self.generate_cache_key(service_name, url)
        cached_video_data = None

        if self.cache is not None and self.cache.has(cache_key):
            cached_video_data = self.cache.get(cache_key)
            self.print(f"[cache]: Video data for {url} loaded from cache.", "suc")

        if cached_video_data is not None:
            video_data = cached_video_data

            if self.ensure_complete_data and not self.is_complete_video_data(video_data):
                resolve(video_data)
                self.save_to_cache(video_data, cache_key, url)

        else:
            # Request phase: Use a capable service to request video data
            # from the URL.
            try:
                self.print(f"[{service_name}]: Requesting data from {url}...")
                video_data = service.request(url)
            except Exception as e:
                self.print(f"[{service_name}]: Request error: {e}", "err")
                raise e
            
            if self.ensure_complete_data and not self.is_complete_video_data(video_data):
                resolve(video_data)

            self.save_to_cache(video_data, cache_key, url)

        # Parse phase: If the service managed to retrieve video data, use it
        # to parse any fields into objects that couldn't have been serialized during the request phase.
        try:
            parsed_video_data = service.parse(video_data)
        except Exception as e:
            self.print(f"[{service_name}]: Parse error: {e}", "err")
            raise e

        return parsed_video_data

    def set_cache(self, cache):
        """Set the fetcher to use a cache object. Fetched video data will be
        stored in the cache.
        """
        self.cache = cache

    def generate_cache_key(self, service_name: str, url: str):
        """Generate a cache key for a given service+url combination. This allows
        us to cache successful responses from a given service for a given URL.
        (It would be nice if we could use tuple keys, but JSON doesn't support
        them).
        """
        return f"{service_name}-{url}"
    
    def save_to_cache(self, video_data, cache_key, url):
        # If using a cache, and if the response object is JSON-serializable,
        # cache the response object so we don't need to retrieve it again.
        if self.cache is None: return

        try:
            self.cache.set(cache_key, video_data)
        except TypeError as e:
            # If we can't cache the response (because the response isn't
            # JSON-serializable), give a warning, but continue.
            self.print(
                f"[cache]: Unable to cache video data from URL {url}; {e}", "err"
            )
    
    def is_complete_video_data(self, video_data: dict):
        return all(val is not None for val in video_data.values())

    def set_printer(self, printer):
        """Set the fetcher to use a printer. Output will be sent to the printer."""
        self.printer = printer

    def print(self, text: str, msg_type: str = "inf"):
        """Output a message to the printer, if available."""
        if self.printer is not None:
            self.printer.print(text, msg_type)
