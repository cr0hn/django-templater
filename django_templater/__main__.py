import os
import glob
import shutil
import argparse
import tempfile

from typing import Tuple
from urllib.parse import urlparse

import requests

from lxml import html


def extract_assets(base_path: str, html_content: str, static_folder: str, download_remote: bool) -> Tuple[bool, str]:
    """
    This function extracts all the assets from an HTML page. Assets are CSS and JS files.

    Those assets will be transformed into Django static files.

    If assets are found it returns True, else it returns False.

    :param html_content:
    :param base_path: Base path of the HTML page
    :param static_folder: Path of the static folder
    :param download_remote: Download remote files

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

    tree = html.fromstring(html_content)

    # Search for CSS files
    css_files = tree.xpath('//link[@rel="stylesheet"]/@href')

    # Search for JS files
    js_files = tree.xpath('//script[@src]/@src')

    # Search for images
    img_files = tree.xpath('//img/@src')

    # If no assets are found, return False
    if not css_files and not js_files and not img_files:
        return False

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
                shutil.copy(origin, destination)

                # Replace the asset path in the HTML page
                html_content = html_content.replace(asset, f"{{% static '{asset_type}/{asset_name}' %}}")

    return True if assets else False, html_content


def fetch_html(url: str) -> str:
    """
    This function fetches the HTML content from a URL or a file.

    :param url: URL or path of the HTML page
    :return: HTML content
    """
    if url.startswith('http://') or url.startswith('https://'):
        return requests.get(url).text
    else:
        with open(url, 'r') as file:
            return file.read()


def convert_to_django_template(page_path: str, block_name: str, output_dir: str, static_folder: str, download_remote: bool):
    """
    This function converts an HTML page to a Django template.

    :param page_path: URL or path of the HTML page
    :param block_name: ID of the Django HTML block to replace
    :param output_dir: Output directory
    :param static_folder: Path of the static folder
    :param download_remote: Download remote files

    :return: Django template
    """
    block = f"{{% block {block_name} %}}"

    html_content = fetch_html(page_path)

    # If the HTML page already contains Django blocks, return
    if block in html_content:
        return

    tree = html.fromstring(html_content)

    # Obtains the content of the block
    block_content = tree.xpath(f"//*[@id='{block_name}']")

    if not block_content:
        raise ValueError(f"Block with ID '{block_name}' not found in HTML page")

    content = html.tostring(block_content[0]).decode() if block_content else ''

    # Extract assets
    base_assets_path = os.path.dirname(page_path)
    found, content = extract_assets(base_assets_path, content, static_folder, download_remote)

    if found:
        header = f"{{% load static %}}\n"
    else:
        header = ''

    text = f"{{% extends 'base.html' %}}\n{header}\n{{% block {block_name} %}}\n{content}\n{{% endblock %}}"

    # Save the Django template
    template_name, _ = os.path.splitext(os.path.basename(page_path))

    with open(os.path.join(output_dir, template_name + '.html'), 'w') as f:
        f.write(text)


def create_django_base_template(master_page_path: str, block_name: str, output_dir: str, static_folder: str, download_remote: bool):
    """
    This function converts an HTML page to a Django template.

    :param master_page_path: URL or path of the master HTML page
    :param block_name: ID of the Django HTML block to replace
    :param output_dir: Output directory
    :param static_folder: Path of the static folder
    :param download_remote: Download remote files

    :return: Django template
    """
    block = f"{{% block main %}}{{% endblock %}}"

    # Get the HTML content
    html_content = fetch_html(master_page_path)

    # Checks if html_content is already a Django template
    if block in html_content:
        return

    # Converts the HTML content to a Django template
    tree = html.fromstring(html_content)

    # Search for block content if block_name is provided
    block_content = tree.xpath(f"//*[@id='{block_name}']")

    if not block_content:
        raise ValueError(f"Block with ID '{block_name}' not found in HTML page")

    # Remove next found block content
    try:
        block_content = block_content[0]
    except IndexError:
        raise ValueError(f"Block with ID '{block_name}' not found in HTML page")

    # Remove children of the block
    for child in block_content.getchildren():
        block_content.remove(child)

    # Add new child to the block
    block_content.text = block

    # Get root element
    root = block_content.getroottree()

    # Resulting HTML
    result = html.tostring(root).decode()

    # Extract assets
    base_assets_path = os.path.dirname(master_page_path)
    found, result = extract_assets(base_assets_path, result, static_folder, download_remote)

    if found:
        result = f"{{% load static %}}\n{result}"

    # Replace all blocks with Django blocks
    with open(os.path.join(output_dir, "base.html"), 'w') as f:
        f.write(result)


def main():
    parser = argparse.ArgumentParser(description='Django Templater')
    parser.add_argument('-b', '--block', help='ID of the HTML block to replace', required=True)
    parser.add_argument('-o', '--output', help='Output directory', default='templates')
    parser.add_argument('-m', '--master-page', help='URL or path of the master HTML page', required=True)
    parser.add_argument('-s', '--static-folder', help='path for assets and statics files', default='static')
    parser.add_argument('other_pages', nargs='*', help='URLs or paths of other HTML pages')
    parser.add_argument('-D', '--download-remote', help='Download remote files', action='store_true', default=False)
    args = parser.parse_args()

    #
    # Variables
    #
    block = args.block
    output_dir = args.output
    master_html = args.master_page
    static_folder = args.static_folder
    download_remote = args.download_remote

    pages = []
    for p in args.other_pages:
        pages.append(*glob.glob(p))

    # Create output templates directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process static page
    static_path = os.path.join(output_dir, static_folder)
    if not os.path.exists(static_path):
        os.makedirs(static_path)

    #
    # Convert the master page to a Django template
    #

    ## Checks if the master template exists
    if not os.path.exists(args.master_page):
        raise ValueError(f"Master page '{args.master_page}' not found")

    ## Checks if the master template is already a Django template or create it
    create_django_base_template(master_html, block, output_dir, static_path, download_remote)

    # Process other pages
    for page in pages:

        # Convert the HTML page to a Django template
        convert_to_django_template(page, block, output_dir, static_path, download_remote)


if __name__ == '__main__':
    main()
