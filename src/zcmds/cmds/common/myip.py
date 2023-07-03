import sys
from typing import Optional

import requests  # type: ignore


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
    print(get_public_ip4())
    return 0


if __name__ == "__main__":
    sys.exit(main())
