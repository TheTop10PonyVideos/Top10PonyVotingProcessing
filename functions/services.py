from functions.general import load_text_data
from functions.config import load_config_json
from functions.messages import suc, inf, err
from classes.fetcher import Fetcher
from classes.fetch_services import YouTubeFetchService, YtDlpFetchService, DerpibooruFetchService, BilibiliFetchService
from classes.caching import FileCache
from classes.printers import ConsolePrinter


def get_fetcher(youtube_api_key: str = None) -> Fetcher:
    """Return a video fetcher instance preconfigured for
    fetching the required video data needed for processing."""

    inf("* Configuring video data fetcher...")
    config = load_config_json("config/config.json")

    fetcher = Fetcher()
    fetcher.set_printer(ConsolePrinter())

    # If configured, set up a cache file for video data
    if (cache_file := config["paths"]["cache"]) is not None:
        inf(f"  * Fetched video data will be cached in {cache_file}.")
        fetcher.set_cache(FileCache(cache_file))

    # Configure fetch services
    inf("  * Adding fetch services...")

    accepted_domains = load_text_data(config["paths"]["accepted_domains"])

    ytdlp_fetch_service = YtDlpFetchService(accepted_domains)

    fetch_services = {
        "YouTube": YouTubeFetchService(youtube_api_key),
        "Bilibili": BilibiliFetchService(ytdlp_fetch_service),
        "Derpibooru": DerpibooruFetchService(),
        "yt-dlp": ytdlp_fetch_service,
    }

    for name, service in fetch_services.items():
        inf(f'    * Adding "{name}" fetch service.')
        fetcher.add_service(name, service)

    suc(f"  * {len(fetch_services)} fetch services added.")

    return fetcher
