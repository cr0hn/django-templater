import os
import glob
import shutil
import tempfile

from typing import List, Tuple
from urllib.parse import urlparse

import requests

from lxml import html


def scan_pages(pages: List[str]) -> List[str]:
    result = []

    for p in pages:
        result.extend([
            x

            for x in
            glob.glob(p)

            if os.path.isfile(x) and (x.endswith('.html') or x.endswith('.htm'))
        ])

    return result

def fetch_html(url: str) -> str:
    """
    This function fetches the HTML content from a URL or a file.

    :param url: URL or path of the HTML page
    :return: HTML content
    """
    if url.startswith('http://') or url.startswith('https://') or url.startswith('//'):
        return requests.get(url).text

    else:
        with open(url, 'r') as file:
            return file.read()


def extract_assets(
        base_path: str, html_content: str, static_folder: str, download_remote: bool, copy_assets: bool = True
) -> Tuple[bool, str | None]:
    """
    This function extracts all the assets from an HTML page. Assets are CSS and JS files.

    Those assets will be transformed into Django static files.

    If assets are found it returns True, else it returns False.

    :param base_path: Base path of the HTML page
    :param html_content: HTML content or path of the HTML page
    :param static_folder: Path of the static folder
    :param download_remote: Download remote files
    :param copy_assets: Copy assets to the static folder

    :return: True if assets are found, False otherwise
    """

    def is_remote_file(path: str) -> bool:
        """
        This function checks if a file is a remote file.

        :param path: Path of the file
        :return: True if the file is remote, False otherwise
        """
        return path.startswith('http://') or path.startswith('https://') or path.startswith('//')

    def extract_remote_name(url: str, asset_type: str) -> str:
        """
        This function extracts the name of a remote file.

        :param url: URL of the remote file
        :param asset_type: Type of the asset

        :return: Name of the remote file
        """
        parsed = urlparse(url)

        name = os.path.basename(parsed.path)

        if not name:
            name = os.path.basename(parsed.hostname)

            # Get only the first part of the host name
            split_name = name.split('.')

            # Like: google.com
            if len(split_name) == 2:
                name = split_name[0]

            # Like: www.google.com
            elif len(split_name) > 2:
                name = split_name[-2]

            # Like: google
            else:
                name = split_name[0]

        _, extension = os.path.splitext(name)

        if asset_type == "css" and extension != ".css":
            name = f"{name}.css"

        elif asset_type == "js" and extension != ".js":
            name = f"{name}.js"

        return name

    # Parse the HTML content
    tree = html.fromstring(html_content)

    # Search for CSS files
    css_files = tree.xpath('//link[@rel="stylesheet"]/@href')

    # Search for JS files
    js_files = tree.xpath('//script[@src]/@src')

    # Search for images
    img_files = tree.xpath('//img/@src')

    # If no assets are found, return False
    if not css_files and not js_files and not img_files:
        return False, None

    assets = {
        'css': css_files,
        'js': js_files,
        'img': img_files
    }

    # Get CSS files
    for asset_type, asset_list in assets.items():

        if not os.path.exists(os.path.join(static_folder, asset_type)):
            os.makedirs(os.path.join(static_folder, asset_type))

        for asset in asset_list:

            # Checks if the asset is a local file
            if is_remote_file(asset) and not download_remote:
                continue

            with tempfile.NamedTemporaryFile() as temp_file:

                if is_remote_file(asset) and download_remote:
                    # Download the asset
                    try:
                        data = requests.get(asset).content
                    except requests.exceptions.ConnectionError:
                        print(f"[!] Error: Unable to download '{asset}'")
                        continue

                    temp_file.write(data)
                    temp_file.flush()

                    origin = temp_file.name
                    asset_name = extract_remote_name(asset, asset_type)
                    destination = os.path.join(static_folder, asset_type, asset_name)

                else:
                    asset_name = os.path.basename(asset)
                    origin = os.path.join(base_path, asset)
                    destination = os.path.join(static_folder, asset_type, asset_name)

                # Copy the asset to the static folder
                if copy_assets:
                    shutil.copy(origin, destination)

                # Replace the asset path in the HTML page
                html_content = html_content.replace(asset, f"{{% static '{asset_type}/{asset_name}' %}}")

    return True if assets else False, html_content


__all__ = (
    'extract_assets',
    'fetch_html',
    'scan_pages',
)
