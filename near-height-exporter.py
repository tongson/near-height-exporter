from urllib.parse import urlparse
import time
import argparse
import requests
import prometheus_client

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
    resp = requests.get(url=url)
    data = resp.json()
    height = data["blocks"][0]["block_height"]
    return float(height)
    
if __name__ == '__main__':
    args = read_args()
    prometheus_client.start_http_server(args.port)
    while True:
        register = prometheus_client.Gauge('near_latest_block_height',
                                           'Near Latest Block Height',
                                           ['remote_api'])
        register.labels(urlparse(args.url).hostname).set(get_height(args.url))
        time.sleep(args.freq)
