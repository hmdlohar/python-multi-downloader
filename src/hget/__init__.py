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
            # Check for url:dir format. 
            # We look for the last ':' that isn't part of the protocol (http://)
            if ":" in item:
                # heuristic: if '://' is present, look for ':' after that
                protocol_idx = item.find("://")
                search_start = protocol_idx + 3 if protocol_idx != -1 else 0
                mapping_idx = item.find(":", search_start)
                
                if mapping_idx != -1:
                    url = item[:mapping_idx]
                    dest_dir = item[mapping_idx+1:]
                    normalized_items.append({
                        "url": url,
                        "dir": resolve_path(dest_dir, global_dest)
                    })
                    continue
            
            normalized_items.append({
                "url": item,
                "dir": global_dest
            })
        elif isinstance(item, (list, tuple)):
            normalized_items.append({
                "url": item[0],
                "dir": resolve_path(item[1], global_dest) if len(item) > 1 else global_dest
            })
        elif isinstance(item, dict):
            normalized_items.append({
                "url": item["url"],
                "dir": resolve_path(item.get("dir") or item.get("dest") or global_dest, global_dest),
                "out": item.get("out")
            })

    # Fix for Jupyter/Colab where event loop is already running
    coro = run_download(normalized_items, use_aria2=use_aria2, max_concurrency=max_concurrency)
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            loop.run_until_complete(coro)
    except RuntimeError:
        # No loop running, safe to use asyncio.run
        asyncio.run(coro)

__all__ = ["download"]
