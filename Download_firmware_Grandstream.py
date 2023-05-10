import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import zipfile
import shutil
from concurrent.futures import ThreadPoolExecutor
import os
from urllib.parse import urljoin
import time


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

# Function to delete all files and directories inside a given folder
def clear_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            os.remove(os.path.join(root, file))
        for directory in dirs:
            shutil.rmtree(os.path.join(root, directory))

# Function to delete a file given its path
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted.")
    except OSError as e:
        print(f"Error deleting file '{file_path}': {e}")

# Function to save a list of links into a file
def save_links_to_file(links, file_path):
    with open(file_path, "w") as file:
        for link in links:
            file.write(f"{link}\n")

# Function to load links from a given file
def load_links_from_file(file_path):
    with open(file_path, "r") as file:
        return [link.strip() for link in file.readlines()]

# Main function to download files from a page and extract certain files from those downloads
def download_files_from_page(url, folder, output_folder, links_file):
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

    save_links_to_file(download_urls, links_file)
    download_urls = load_links_from_file(links_file)

    download_count = len(download_urls)
    extracted_count = 0
    downloaded_files = []
    extracted_files = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in download_urls:
            try:
                downloaded_file = download_file(url, folder)
                downloaded_files.append(os.path.basename(downloaded_file))
                extracted_count += extract_files_from_zip(downloaded_file, output_folder)

                for filename in os.listdir(output_folder):
                    if filename.endswith(".bin"):
                        extracted_files.append(filename)
            except Exception as e:
                print(f"Error processing URL '{url}': {e}")

    print(f"Downloads: {download_count}")
    print(f"Extracted firmware files: {extracted_count}")

    print("Script execution completed.")



if __name__ == "__main__":
    url = "https://www.grandstream.com/support/firmware"# URL to download firmware from
    downloaded_files_folder = "~/downloaded_files"# Folder to save downloaded files
    extracted_files_folder = "/var/www/grandstream-firmware"# Folder to save extracted files
    links_file = "firmware_links.txt"# File to save links
    # Clear folders and delete links file before starting download
    clear_folder(downloaded_files_folder)
    clear_folder(extracted_files_folder)
    delete_file(links_file)

    # Record the start time
    start_time = time.time()
    download_files_from_page(url, folder=downloaded_files_folder, output_folder=extracted_files_folder, links_file=links_file)

    # Calculate the elapsed time
    elapsed_time = time.time() - start_time

    # Print the elapsed time
    print(f"Script execution time: {elapsed_time:.2f} seconds")



