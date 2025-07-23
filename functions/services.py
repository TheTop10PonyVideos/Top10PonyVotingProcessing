from functions.general import load_text_data
from functions.config import load_config_json
from functions.messages import suc, inf, err
from classes.fetcher import Fetcher
from classes.fetch_services import YouTubeFetchService, YtDlpFetchService, DerpibooruFetchService
from classes.caching import FileCache
from classes.printers import ConsolePrinter


def get_fetcher(
    youtube_api_key: str = None, ensure_complete_data: bool = False
) -> Fetcher:
    """Return the standard video fetcher used by the Top 10 Pony Videos
    applications (currently configured for YouTube and yt-dlp). This function
    takes configuration directly from the main config file, to avoid the need to
    specify configuration arguments directly.

    Parameters
    ----------
    youtube_api_key : str, optional
        The YouTube API key to be used by the YouTube fetch service
    ensure_complete_data : bool, optional
        Determines the behavior when the response data is missing any necessary
        data.
        If set to True, the execution will be halted and the user will be
        prompted to manually input the missing data.
        By default, it is set to False, so videos will be annotated as missing
        fields instead of halting for manual input
    """

    inf("* Configuring video data fetcher...")
    config = load_config_json("config/config.json")

    fetcher = Fetcher(ensure_complete_data)
    fetcher.set_printer(ConsolePrinter())

    # If configured, set up a cache file for video data.
    cache_file = config["paths"]["cache"]
    if cache_file is not None:
        inf(f"  * Fetched video data will be cached in {cache_file}.")
        fetcher.set_cache(FileCache(cache_file))

    # Configure fetch services. Currently the YouTube Data API and yt-dlp are
    # supported.
    inf("  * Adding fetch services...")

    accepted_domains = load_text_data(config["paths"]["accepted_domains"])

    fetch_services = {
        "YouTube": YouTubeFetchService(youtube_api_key),
        "Derpibooru": DerpibooruFetchService(),
        "yt-dlp": YtDlpFetchService(accepted_domains),
    }

    for name, service in fetch_services.items():
        inf(f'    * Adding "{name}" fetch service.')
        fetcher.add_service(name, service)

    suc(f"  * {len(fetch_services)} fetch services added.")

    return fetcher
