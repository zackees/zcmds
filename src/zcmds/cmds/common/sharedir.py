import argparse
import os
import subprocess
import sys
from typing import Optional

import requests  # type: ignore

PORT = 6789


def get_public_ip4() -> Optional[str]:
    urls = ["https://api.ipify.org", "https://ipv4.icanhazip.com/"]
    for i, url in enumerate(urls):
        try:
            return requests.get(url, timeout=5).text.strip()
        except requests.exceptions.RequestException:
            pass
    print("Unable to get public ip4")
    return None


def main() -> int:
    parser = argparse.ArgumentParser("Arguments for sharedir")
    parser.add_argument("--dir", help="directory to share", default=os.getcwd())
    parser.add_argument(
        "--use-local-tunnel",
        help="use localtunnel instead of ngrok",
        action="store_true",
    )
    args = parser.parse_args()
    os.chdir(args.dir)
    cleanup = []
    if args.use_local_tunnel:
        my_ip4 = get_public_ip4()
        http_proc = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)])
        cleanup.append(lambda: http_proc.kill())
        if my_ip4:
            print(f"Send this IP to the other person: {my_ip4}")
        return os.system(f"lt --port {PORT}")
    try:
        return os.system("ngrok http file:///")
    except KeyboardInterrupt:
        pass
    finally:
        for func in cleanup:
            func()
    return 0


if __name__ == "__main__":
    sys.exit(main())
