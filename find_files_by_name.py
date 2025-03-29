import os
from typing import Optional

from string_content_check import string_content_check as check_file_name


def find_files_by_name(
        directory: str,
        starts_with: Optional[str] = None,
        contains: Optional[str] = None,
        ends_with: Optional[str] = None,
        match_case: bool = False,
        must_pass_all: bool = False, # AND operation
        search_subdir: bool = False
):
    """
    Finds all files in a directory (and optionally subdirectories) that match the given criteria.

    Args:
        directory (str): The directory to search.
        starts_with (str, optional): Filename must start with this string.
        contains (str, optional): Filename must contain this substring.
        ends_with (str, optional): Filename must end with this string.
        match_case (bool): Whether the match is case-sensitive.
        must_pass_all (bool): If True, all criteria must match; otherwise, any match is sufficient.
        search_subdir (bool): Whether to search subdirectories.

    Returns:
        set: A set of full file paths to matching files.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    files_found = set()

    def add_matching_files(dir_path: str, filenames: list):
        for filename in filenames:
            full_path = os.path.join(dir_path, filename)
            if os.path.isfile(full_path) and check_file_name(filename, starts_with, contains, ends_with, match_case, must_pass_all):
                files_found.add(full_path)

    if search_subdir:
        for root, _, filenames in os.walk(directory):
            add_matching_files(root, filenames)
    else:
        add_matching_files(directory, os.listdir(directory))

    return files_found



def main():
    search_directory = r"test"


    print("==== Test 1 ==== ")
    files = find_files_by_name(search_directory)
    for file in files:
        print(file)


    print("==== Test 2 ==== ")
    files = find_files_by_name(search_directory, '.txt')
    for file in files:
        print(file)


    print("==== Test 3 ==== ")
    files = find_files_by_name(search_directory, 'txt')
    for file in files:
        print(file)


    # print("==== Test 4 ==== ")
    # files = find_files_by_name(search_directory, {'txt', '.mp4'})
    # for file in files:
    #     print(file)


    print("==== Test 5 ==== ")
    files = find_files_by_name(search_directory, search_subdir=True)
    for file in files:
        print(file)

if __name__ == "__main__":
    main()