import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Union, Optional

import httpx
from tqdm.rich import tqdm
from rich.console import Console

from .utils import resolve_path, ensure_dir, has_aria2

console = Console()

class Downloader:
    async def download_all(self, items: List[Dict[str, str]], max_concurrency: int = 4):
        raise NotImplementedError

class Aria2Downloader(Downloader):
    async def download_all(self, items: List[Dict[str, str]], max_concurrency: int = 16):
        """Use aria2c to download files using an input file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for item in items:
                url = item['url']
                dest_dir = item['dir']
                f.write(f"{url}\n")
                f.write(f"  dir={dest_dir}\n")
                if 'out' in item:
                    f.write(f"  out={item['out']}\n")
            temp_path = f.name

        try:
            # -j: max concurrent downloads
            # -x: max connections per server
            # -s: split
            cmd = [
                "aria2c", 
                "-i", temp_path, 
                "-j", str(max_concurrency),
                "-x", "16",
                "-s", "16",
                "--console-log-level=warn",
                "--summary-interval=0"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=None,
                stderr=None
            )
            await process.wait()
            
            if process.returncode != 0:
                console.print(f"[bold red]aria2c exited with code {process.returncode}[/bold red]")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

class NativeDownloader(Downloader):
    async def download_file(self, client: httpx.AsyncClient, url: str, dest_dir: Path, filename: Optional[str] = None, semaphore: asyncio.Semaphore = None):
        if semaphore:
            async with semaphore:
                return await self._download(client, url, dest_dir, filename)
        else:
            return await self._download(client, url, dest_dir, filename)

    async def _download(self, client: httpx.AsyncClient, url: str, dest_dir: Path, filename: Optional[str] = None):
        ensure_dir(dest_dir)
        
        try:
            async with client.stream("GET", url, follow_redirects=True) as response:
                if response.status_code != 200:
                    console.print(f"[red]Failed to download {url}: {response.status_code}[/red]")
                    return

                if not filename:
                    # Try to get filename from Content-Disposition or URL
                    filename = response.headers.get("Content-Disposition", "").split("filename=")[-1].strip('"')
                    if not filename:
                        filename = url.split("/")[-1].split("?")[0]
                
                dest_path = dest_dir / filename
                total = int(response.headers.get("Content-Length", 0))

                with open(dest_path, "wb") as f:
                    with tqdm(total=total, unit='B', unit_scale=True, desc=filename, leave=False) as progress:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                            progress.update(len(chunk))
        except Exception as e:
            console.print(f"[red]Error downloading {url}: {e}[/red]")

    async def download_all(self, items: List[Dict[str, str]], max_concurrency: int = 4):
        semaphore = asyncio.Semaphore(max_concurrency)
        async with httpx.AsyncClient(timeout=None) as client:
            tasks = []
            for item in items:
                dest_dir = Path(item['dir'])
                tasks.append(self.download_file(client, item['url'], dest_dir, item.get('out'), semaphore))
            
            await asyncio.gather(*tasks)

async def run_download(items: List[Dict[str, str]], use_aria2: bool = True, max_concurrency: Optional[int] = None):
    if use_aria2 and has_aria2():
        downloader = Aria2Downloader()
        mc = max_concurrency or 16
    else:
        if use_aria2:
            console.print("[yellow]aria2c not found, falling back to native downloader[/yellow]")
        downloader = NativeDownloader()
        mc = max_concurrency or 4
    
    await downloader.download_all(items, max_concurrency=mc)
