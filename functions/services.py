import csv, os
from dotenv import load_dotenv
from classes.fetcher import Fetcher
from classes.fetch_services import YouTubeFetchService, YtDlpFetchService
from classes.caching import FileCache
from classes.printers import ConsolePrinter
from functions.messages import suc, inf, err

# Load environment configuration from a `.env` file if present.
load_dotenv()

API_KEY = os.getenv("apikey")  # may replace this

def get_fetcher() -> Fetcher:
    """Return the standard video fetcher used by the Top 10 Pony Videos
    applications (currently configured for YouTube and yt-dlp)."""

    inf("* Configuring video data fetcher...")
    fetcher = Fetcher()
    fetcher.set_printer(ConsolePrinter())

    # Set up a cache file for video data.
    response_cache_file = os.getenv("response_cache_file")

    if response_cache_file is not None:
        inf(f"  * Fetched video data will be cached in {response_cache_file}.")
        fetcher.set_cache(FileCache(response_cache_file))

    # Configure fetch services. Currently the YouTube Data API and yt-dlp are
    # supported.
    inf("  * Adding fetch services...")
    accepted_domains = []
    with open("modules/csv/accepted_domains.csv", "r") as csvfile:
        reader = csv.reader(csvfile)
        accepted_domains = [row[0] for row in reader]

    fetch_services = {
        "YouTube": YouTubeFetchService(API_KEY),
        "yt-dlp": YtDlpFetchService(accepted_domains),
    }

    for name, service in fetch_services.items():
        inf(f'    * Adding "{name}" fetch service.')
        fetcher.add_service(name, service)

    suc(f"  * {len(fetch_services)} fetch services added.")

    return fetcher


