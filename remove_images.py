#!/usr/local/bin/python3

import os
import re


def get_all_files(media_dir):
    """
    List all files in the directory, excluding certain always-kept files.
    """
    return set(
        [
            file for file in os.listdir(media_dir)
            if file not in {".keep", "banner.png"}
        ]
    )


def extract_media_references(md_content):
    """
    Extract file references from Markdown and HTML content.
    Includes images and other media (e.g., video, audio).
    """
    # Markdown-style media references
    md_references = re.findall(r'!\[.*?\]\(images/(.*?)\)', md_content)

    # HTML-style media references (<img>, <video>, <audio>, <source>)
    html_references = re.findall(
        r'(?:<img|<video|<audio|<source).*?src=["\']images/(.*?)[\'"].*?>',
        md_content
    )

    # Combine and deduplicate references
    all_references = set(md_references + html_references)

    print(f"Extracted references from Markdown/HTML: {all_references}")
    return all_references


def process_directory(en_directory):
    """
    Process a single 'en' directory, archiving unreferenced media files.
    """
    print(f"Processing directory: {en_directory}")

    media_dir = os.path.join(en_directory, 'images')
    archive_dir = os.path.join(media_dir, 'archive')

    # Ensure the archive directory exists
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # Get all files in the media directory
    all_files = get_all_files(media_dir)
    print(f"All files: {all_files}")

    # Find all referenced media files
    referenced_files = set()
    for root, _, files in os.walk(en_directory):
        for file in files:
            if file.endswith('.md'):
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    referenced_files.update(extract_media_references(content))
    print(f"Referenced files: {referenced_files}")

    # Identify unreferenced files
    unreferenced_files = all_files - referenced_files - {'archive'}
    print(f"Unreferenced files: {unreferenced_files}")

    # Move unreferenced files to the archive folder
    for file in unreferenced_files:
        src = os.path.join(media_dir, file)
        dst = os.path.join(archive_dir, file)
        os.rename(src, dst)

    print(f"Moved {len(unreferenced_files)} files to {archive_dir}")


def main():
    """
    Traverse the project directory and process all 'en' directories within.
    """
    # This prompt can be altered when placed higher above the project dir
    repo_directory = input("Enter the path to the project directory (slug): ")

    if not os.path.exists(repo_directory):
        print(f"The project {repo_directory} does not exist there.")
        return

    # Find all 'en' directories under the repo directory
    for root, dirs, _ in os.walk(repo_directory):
        for dir_name in dirs:
            if dir_name == 'en':
                en_directory = os.path.join(root, dir_name)
                process_directory(en_directory)
    print(
        "Check the new archive folder for any media removed in error,\n"
        "then delete the archive folder to prevent issues\n"
        "when pushing the project to GitHub"
    )


if __name__ == "__main__":
    main()
