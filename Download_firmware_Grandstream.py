import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import os
import time
import shutil


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
            os.remove(os.path.join(root, file))
        for directory in dirs:
            shutil.rmtree(os.path.join(root, directory))


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
    downloaded_files_folder = "/Users/aalexeei/PycharmProjects/pythonProject/downloaded_files"  # Folder to save downloaded files

    # Clear folder before starting download
    clear_folder(downloaded_files_folder)

    # Record the start time
    start_time = time.time()
    download_files_from_page(url, folder=downloaded_files_folder)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    # Print the elapsed time
    print(f"Script execution time: {elapsed_time:.2f} seconds")
