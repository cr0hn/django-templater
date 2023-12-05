import os
import glob
import argparse

from lxml import html

from django_templater.shared import fetch_html, extract_assets


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
        pages.extend([
            x

            for x in
            glob.glob(p)

            if os.path.isfile(x) and (x.endswith('.html') or x.endswith('.htm'))
        ])

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
