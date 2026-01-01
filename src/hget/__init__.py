import asyncio
from typing import List, Union, Dict, Optional
import os

from .core import run_download
from .utils import resolve_path

def download(
    items: Union[str, List[Union[str, List[str], Dict[str, str]]]],
    dest: Optional[str] = None,
    parallel: bool = True,
    max_concurrency: Optional[int] = None,
    use_aria2: bool = True
):
    """
    Download multiple URLs in parallel.
    
    Args:
        items: A single URL string, or a list of items. 
               Items can be:
               - "url"
               - ["url", "dest_dir"]
               - {"url": "url", "dir": "dest_dir", "out": "filename"}
        dest: Global destination directory (used if item doesn't specify one).
        parallel: Whether to download in parallel (always True for now in this version).
        max_concurrency: Max number of concurrent downloads.
        use_aria2: Whether to prefer aria2c if available.
    """
    if isinstance(items, str):
        items = [items]
    
    normalized_items = []
    global_dest = dest or os.getcwd()

    for item in items:
        if isinstance(item, str):
            # Check for url:dir format
            if ":" in item and not item.startswith(("http://", "https://", "ftp://")):
                # This logic is a bit tricky since URL contains ':', 
                # but usually at the beginning (https://)
                # Let's split from the right if it looks like a path override
                pass
            
            normalized_items.append({
                "url": item,
                "dir": global_dest
            })
        elif isinstance(item, (list, tuple)):
            normalized_items.append({
                "url": item[0],
                "dir": item[1] if len(item) > 1 else global_dest
            })
        elif isinstance(item, dict):
            normalized_items.append({
                "url": item["url"],
                "dir": item.get("dir") or item.get("dest") or global_dest,
                "out": item.get("out")
            })

    asyncio.run(run_download(normalized_items, use_aria2=use_aria2, max_concurrency=max_concurrency))

__all__ = ["download"]
