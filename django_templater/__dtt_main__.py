import os
import argparse

from django_templater.shared import extract_assets, scan_pages


def main():
    parser = argparse.ArgumentParser(description='Django Templater - Convert HTML assets links to Django templates')
    parser.add_argument('-o', '--output', help='Output directory', default=None)
    parser.add_argument('-s', '--static-folder', help='path for assets and statics files', default='static')
    parser.add_argument('other_pages', nargs='*', help='URLs or paths of other HTML pages')
    parser.add_argument('-D', '--download-remote', help='Download remote files', action='store_true', default=False)
    parser.add_argument('-c', '--copy-assets', help='Copy assets to the static folder', action='store_true', default=False)
    args = parser.parse_args()

    if not args.other_pages:
        parser.error('No HTML page specified')

    #
    # Variables
    #
    output_dir = args.output
    copy_assets = args.copy_assets
    static_folder = args.static_folder
    download_remote = args.download_remote
    pages = scan_pages(args.other_pages)

    # Create output templates directory if it doesn't exist
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # Process static page
    if output_dir:
        static_path = os.path.join(output_dir, static_folder)
    else:
        static_path = static_folder

    if not os.path.exists(static_path):
        os.makedirs(static_path)

    # Process other pages
    for page in pages:

        # Read origin
        with open(page, 'r') as file:
            html_content = file.read()

        # Extract assets
        _, fixed_html_content = extract_assets(os.path.dirname(page), html_content, static_path, download_remote, copy_assets=copy_assets)

        # Write fixed HTML to destination
        if output_dir is None:
            print(fixed_html_content)

        else:

            output_path = os.path.join(output_dir, os.path.basename(page))
            with open(output_path, 'w') as file:
                file.write(fixed_html_content)


if __name__ == '__main__':
    main()
