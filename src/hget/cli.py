import argparse
import sys
import os
from . import download

def parse_item(item: str, default_dir: str):
    """Parse item in format 'url:dir' or just 'url'."""
    # We need to be careful with URLs like https://...
    # If the string contains a ':' AFTER the protocol part, it might be a mapping
    
    parts = item.rsplit(":", 1)
    if len(parts) == 2:
        url, dest = parts
        # If url doesn't look like it has a protocol or if it ends with a protocol, 
        # it might not be a mapping.
        # But rsplit(":", 1) handles things like https://example.com/file:./dir
        if url.startswith(("http", "ftp")) and "/" not in parts[1]:
            # Likely just a URL (e.g. http://host:8080/path)
            # This is a heuristic.
            return {"url": item, "dir": default_dir}
        return {"url": url, "dir": dest}
    return {"url": item, "dir": default_dir}

def main():
    parser = argparse.ArgumentParser(description="hget: High-performance parallel downloader")
    parser.add_argument("urls", nargs="+", help="URLs to download. Format: 'url' or 'url:dest_dir'")
    parser.add_argument("-d", "--dir", default=".", help="Global destination directory")
    parser.add_argument("-j", "--jobs", type=int, help="Max concurrent downloads")
    parser.add_argument("--no-aria2", action="store_false", dest="use_aria2", help="Disable aria2c and use native downloader")
    parser.set_defaults(use_aria2=True)

    args = parser.parse_args()

    items = []
    for url_arg in args.urls:
        items.append(parse_item(url_arg, args.dir))

    try:
        download(
            items, 
            dest=args.dir, 
            max_concurrency=args.jobs, 
            use_aria2=args.use_aria2
        )
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
