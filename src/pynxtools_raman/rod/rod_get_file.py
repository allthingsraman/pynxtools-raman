import argparse

import requests


rod_id = 1000679


def save_rod_file_from_ROD_via_API(rod_id: int) -> str:
    url = "https://solsa.crystallography.net/rod/" + str(rod_id) + ".rod"
    response = requests.post(url)

    filename = str(rod_id)

    with open(filename + ".rod", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("Saved ROD ID %s to file '%s'"(rod_id, filename))


def trigger_rod_download():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Download a CIF file.")
    parser.add_argument(
        "rod_id",  # The argument's name
        type=str,  # Argument type (e.g., string)
        help="The name of the file to download",  # Help message
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    save_rod_file_from_ROD_via_API(args.rod_id)

    # Use the parsed argument
    print(f"Downloading CIF file: {args.rod_id}")
    # Add your logic to download the file here
