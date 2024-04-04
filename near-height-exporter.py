from urllib.parse import urlparse
import time
import argparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import prometheus_client
from prometheus_client import REGISTRY

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporter of external Near block height.")
    parser.add_argument("--port",
                        metavar="PORT",
                        type=int,
                        default=9099,
                        help="The port used to export the metrics. Default is 9099.")
    parser.add_argument("--url",
                        metavar="URL",
                        default=False,
                        type=str,
                        help="URL of Near API endpoint.")
    parser.add_argument("--freq",
                        metavar="FREQ",
                        type=int,
                        default=300,
                        help="Update frequency in seconds. Default is 300 seconds (5 minutes).")
    return parser.parse_args()

def get_height(url: str) -> float:
    retry_strategy = Retry(
        total=4,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount('https://', adapter)
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        height = data["blocks"][0]["block_height"]
        return float(height)
    else:
        return float(0)
    
if __name__ == '__main__':
    args = read_args()
    for coll in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(coll)
    prometheus_client.start_http_server(args.port)
    while True:
        height = get_height(args.url)
        if height > 1:
            register = prometheus_client.Gauge('near_latest_block_height',
                                               'Near Latest Block Height',
                                               ['external_url'])
            register.labels(urlparse(args.url).hostname).set(height)
        time.sleep(args.freq)
