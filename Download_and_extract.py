import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import os
import time
import shutil
import zipfile


# Function to check if a url is valid
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


# Function to download a file from a given url and save it into a folder
def download_file(url, folder):
    response = requests.get(url, stream=True)
    file_name = os.path.join(folder, url.split("/")[-1])
    with open(file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
    return file_name


# Function to delete all files and directories inside a given folder
def clear_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if not file.endswith(".xml"):
                os.remove(os.path.join(root, file))
        for directory in dirs:
            shutil.rmtree(os.path.join(root, directory))


# Function to extract .bin files from a given zip file and save them into an output folder
def extract_files_from_zip(zip_file, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    extracted_count = 0
    with zipfile.ZipFile(zip_file, "r") as zf:
        for member in zf.infolist():
            if not os.path.isdir(member.filename) and member.filename.endswith(".bin"):
                filename = os.path.basename(member.filename)
                with zf.open(member) as source, open(os.path.join(output_folder, filename), "wb") as target:
                    shutil.copyfileobj(source, target)
                print(f"Extracted: {filename}")
                extracted_count += 1
    return extracted_count


# Main function to download files from a page
def download_files_from_page(url, folder):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    if not os.path.exists(folder):
        os.makedirs(folder)

    download_urls = []
    for tag in soup.find_all("a"):
        href = tag.get("href")

        full_url = urljoin(url, href)

        if href and is_valid(full_url) and not href.startswith("#") and full_url.endswith(".zip"):
            print(f"Link: {full_url}")  # Print the link
            download_urls.append(full_url)

    download_count = len(download_urls)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in download_urls:
            try:
                download_file(url, folder)
            except Exception as e:
                print(f"Error processing URL '{url}': {e}")

    print(f"Downloads: {download_count}")
    print("Download script execution completed.")


if __name__ == "__main__":
    url = "https://www.grandstream.com/support/firmware"  # URL to download firmware from
    downloaded_files_folder = "./downloaded_files"  # Folder to save downloaded files
    extracted_files_folder = "./extracted_files"  # Folder to save extracted files

    # Clear folders before starting download and extraction
    clear_folder(downloaded_files_folder)
    clear_folder(extracted_files_folder)

    # Record the start time
    start_time = time.time()

    # Download files from the page
    download_files_from_page(url, folder=downloaded_files_folder)

    extracted_count = 0
    corrupted_files = []

    # Iterate over all files in the downloaded_files_folder
    for filename in os.listdir(downloaded_files_folder):
        if filename.endswith(".zip"):
            downloaded_file = os.path.join(downloaded_files_folder, filename)

            # Check if the ZIP file is valid
            try:
                with zipfile.ZipFile(downloaded_file, "r") as test_zip:
                    test_zip.testzip()
            except zipfile.BadZipFile:
                print(f"Skipping corrupted file: {filename}")
                corrupted_files.append(filename)
                continue

            # Extract files from the ZIP file
            extracted_count += extract_files_from_zip(downloaded_file, extracted_files_folder)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    print(f"Downloads: {len(os.listdir(downloaded_files_folder))}")
    print(f"Extracted firmware files: {extracted_count}")
    print("Corrupted files: ", corrupted_files)
    print(f"Script execution time: {elapsed_time:.2f} seconds")
    print("Extraction script execution completed.")


