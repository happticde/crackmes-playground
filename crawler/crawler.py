#!/opt/venv/bin/python
"""
A script to scrape crackme details from crackmes.one.
"""

import argparse
import os
import sys
import re  # Import re for regex matching
from typing import Dict, Optional
from urllib.parse import urljoin
import zipfile

import requests
from bs4 import BeautifulSoup, Tag

# --- Constants ---
BASE_URL = "https://crackmes.one"
USER_AGENT = "Mozilla/5.0"


def get_soup(url: str) -> Optional[BeautifulSoup]:
    """Fetch the URL and return a BeautifulSoup object."""
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch URL {url}. Reason: {e}", file=sys.stderr)
        return None


def download_file(url: str, directory: str = ".") -> Optional[str]:
    """Download a file from a URL into a specified directory."""
    try:
        response = requests.get(url, stream=True, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        filename = url.split("/")[-1]
        filepath = os.path.join(directory, filename)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filename}")
        return filepath
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not download file {url}. Reason: {e}", file=sys.stderr)
        return None


def unzip_file(
    zip_filepath: str, password: Optional[str] = None, extract_dir: Optional[str] = None
) -> bool:
    """
    Unzips a password-protected zip file.
    Returns True on success, False on failure.
    """
    if extract_dir is None:
        base_extract_dir = os.path.dirname(zip_filepath)
    else:
        base_extract_dir = extract_dir

    final_extract_dir = os.path.join(
        base_extract_dir, "crackme"
    )  # Always extract to 'crackme' subdirectory
    os.makedirs(final_extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_filepath, "r") as zf:
            if password:
                zf.extractall(path=final_extract_dir, pwd=password.encode("utf-8"))
            else:
                zf.extractall(path=final_extract_dir)

            print(f"Successfully unzipped {zip_filepath} to {final_extract_dir}")

            # Recursive unzipping
            for member in zf.namelist():
                member_path = os.path.join(final_extract_dir, member)
                if os.path.isfile(member_path) and member_path.lower().endswith(".zip"):
                    print(
                        f"Found nested zip file: {member_path}. Attempting to unzip recursively."
                    )
                    # Recursively call unzip_file, passing the current final_extract_dir as the base for the next 'crackme' dir
                    unzip_file(
                        member_path, password, final_extract_dir
                    )  # Pass password for nested zips too

            return True
    except zipfile.BadZipFile:
        print(f"Error: {zip_filepath} is a bad zip file.", file=sys.stderr)
    except RuntimeError as e:  # For incorrect password
        print(
            f"Error unzipping {zip_filepath}: {e}. Incorrect password?", file=sys.stderr
        )
    except Exception as e:
        print(
            f"An unexpected error occurred while unzipping {zip_filepath}: {e}",
            file=sys.stderr,
        )
    return False


def generate_markdown(title: str, details: Dict[str, str], description: str) -> str:
    """Generate the markdown content from the scraped data."""
    md_parts = [f"# {title}\n", "## Details\n"]
    for key, value in details.items():
        md_parts.append(f"- **{key}:** {value}")

    md_parts.append("\n## Description\n")
    # Handle multi-line description by prepending "> " to each line
    formatted_description_text = "\n".join(
        [f"> {line}" for line in description.splitlines()]
    )
    md_parts.append(f"{formatted_description_text}\n")

    return "\n".join(md_parts)


def scrape_crackme(
    crackme_id: str, output_dir: str, password: Optional[str] = None
) -> None:
    """Scrape a crackme page and save the details."""
    url = f"{BASE_URL}/crackme/{crackme_id}"
    print(f"Scraping {url}...")
    soup = get_soup(url)
    if not soup:
        sys.exit(1)

    # --- Extract Title and Author from <h3> tag ---
    # The structure is <h3><a href="/user/mirunaf">mirunaf</a>'s Very easy</h3>
    h3_tag = soup.find("h3")
    if not isinstance(h3_tag, Tag):
        print("Error: Could not find main title/author tag.", file=sys.stderr)
        sys.exit(1)

    full_title_text = h3_tag.text.strip()

    # Extract author (text before 's)
    author_match = re.match(r"^(.*?)'s (.*)$", full_title_text)
    if author_match:
        author = author_match.group(1).strip()
        title = author_match.group(2).strip()
    else:
        author = "Unknown"
        title = full_title_text  # Fallback if format is different

    # Fix: Replace spaces with underscores for safe directory names
    safe_title_for_dir = title.replace(" ", "_")
    safe_title_for_dir = "".join(
        c for c in safe_title_for_dir if c.isalnum() or c in ("_",)
    ).rstrip()

    # Construct folder title as author_title
    folder_name = f"{author.replace(' ', '_')}_{safe_title_for_dir}"
    crackme_dir = os.path.join(output_dir, folder_name)
    os.makedirs(crackme_dir, exist_ok=True)

    # --- Extract Details ---
    details = {}
    # Details are in <p> tags within <div class="column col-3"> inside <div class="columns panel-background">
    panel_background_div = soup.find("div", class_="columns panel-background")
    if isinstance(panel_background_div, Tag):
        detail_columns = panel_background_div.find_all("div", class_="column col-3")
        for col in detail_columns:
            p_tag = col.find("p")
            if p_tag and p_tag.text.strip().startswith(
                "Author:"
            ):  # Handle the explicit Author: line first
                key = "Author"
                value = p_tag.find("a").text.strip()
                details[key] = value
            elif p_tag and p_tag.find("br"):
                key = p_tag.contents[0].strip().replace(":", "")
                value = p_tag.find("br").next_sibling.strip()
                details[key] = value

    # --- Extract Description ---
    description = ""
    # Description is in a <p> tag following a <p><b>Description</b></p>
    description_header_p = soup.find(
        "p",
        string=lambda text: text
        and "Description" in text
        and text.strip() == "Description",
    )
    if isinstance(description_header_p, Tag):
        description_span = description_header_p.find_next_sibling("p")
        if isinstance(description_span, Tag):
            # The actual text is inside a span with style="white-space: pre-line"
            final_description_text = description_span.find(
                "span", style="white-space: pre-line"
            )
            if isinstance(final_description_text, Tag):
                description = final_description_text.text.strip()
            else:
                description = (
                    description_span.text.strip()
                )  # Fallback if span not found

    # --- Download File ---
    download_link = soup.find(
        "a", class_="btn-download"
    )  # Use class for more specific selection
    if isinstance(download_link, Tag):
        download_url = urljoin(BASE_URL, download_link["href"])
        print(f"Found download link: {download_url}")
        zip_filepath = download_file(download_url, directory=crackme_dir)
        if zip_filepath:
            unzipped = False
            if password:
                print(f"Attempting to unzip with provided password: '{password}'")
                unzipped = unzip_file(zip_filepath, password=password)

            if not unzipped:
                default_passwords = ["crackmes.one", "crackmes.de"]
                for default_pwd in default_passwords:
                    print(f"Attempting to unzip with default password: '{default_pwd}'")
                    unzipped = unzip_file(zip_filepath, password=default_pwd)
                    if unzipped:
                        break

            if not unzipped:
                print(
                    f"Warning: Could not unzip {zip_filepath} with any provided or default passwords. Trying without password.",
                    file=sys.stderr,
                )
                if not unzip_file(zip_filepath):
                    print(
                        f"Warning: Could not unzip {zip_filepath} without password.",
                        file=sys.stderr,
                    )
    else:
        print("Warning: Could not find download link.", file=sys.stderr)

    # --- Generate and Save Markdown ---
    md_content = generate_markdown(title, details, description)
    md_filename = os.path.join(crackme_dir, "README.md")
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Successfully created markdown file: {md_filename}")
    except IOError as e:
        print(
            f"Error: Could not write to file {md_filename}. Reason: {e}",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    """Parse command-line arguments and run the scraper."""
    parser = argparse.ArgumentParser(description="Scrape a crackme from crackmes.one.")
    parser.add_argument(
        "id", help="The ID of the crackme to scrape (e.g., 685048992b84be7ea7743940)."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="crackmes",
        help="Output directory to save crackme folder.",
    )
    parser.add_argument(
        "-p",
        "--password",
        help="Password for the zip archive (if protected).",
    )
    args = parser.parse_args()
    scrape_crackme(args.id, args.output, args.password)


if __name__ == "__main__":
    main()
