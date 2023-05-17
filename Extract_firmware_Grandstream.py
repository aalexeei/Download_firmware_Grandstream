import os
import zipfile
import shutil


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


if __name__ == "__main__":
    downloaded_files_folder = "/Users/aalexeei/PycharmProjects/pythonProject/downloaded_files"  # Folder with downloaded files
    #extracted_files_folder = "/var/www/grandstream-firmware"  # Folder to save extracted files
    extracted_files_folder = "/Users/aalexeei/PycharmProjects/pythonProject/extracted_files"
    # Clear folder before starting extraction
    clear_folder(extracted_files_folder)

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

            extracted_count += extract_files_from_zip(downloaded_file, extracted_files_folder)

    print(f"Extracted firmware files: {extracted_count}")
    print("Corrupted files: ", corrupted_files)
    print("Extraction script execution completed.")
