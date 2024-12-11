import os
import shutil
import urllib.request
import zipfile

import static_assets


def build_govuk_assets(static_dist_root="frontend/static/dist"):

    DIST_ROOT = "./" + static_dist_root
    GOVUK_URL = "https://github.com/alphagov/govuk-frontend/releases/download/v4.8.0/release-v4.8.0.zip"
    ZIP_FILE = "./govuk_frontend.zip"
    DIST_PATH = DIST_ROOT
    ASSETS_DIR = "/assets"
    ASSETS_PATH = DIST_PATH + ASSETS_DIR

    # Checks if GovUK Frontend Assets already built
    if os.path.exists(DIST_PATH):
        print("GovUK Frontend assets already built.If you require a rebuild manually run build.build_govuk_assets")
        return True

    # Download zips from GOVUK_URL
    # There is a known problem on Mac where one must manually
    # run the script "Install Certificates.command" found
    # in the python application folder for this to work.

    print("Downloading static file zip.")
    urllib.request.urlretrieve(GOVUK_URL, ZIP_FILE)  # nosec

    # Attempts to delete the old files, states if
    # one doesn't exist.

    print("Deleting old " + DIST_PATH)
    try:
        shutil.rmtree(DIST_PATH)
    except FileNotFoundError:
        print("No old " + DIST_PATH + " to remove.")

    # Extract the previously downloaded zip to DIST_PATH

    print("Unzipping file to " + DIST_PATH + "...")
    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(DIST_PATH)

    # Move files from ASSETS_PATH to DIST_PATH

    print("Moving files from " + ASSETS_PATH + " to " + DIST_PATH)
    for file_to_move in os.listdir(ASSETS_PATH):
        shutil.move("/".join([ASSETS_PATH, file_to_move]), DIST_PATH)

    # Delete temp files
    print("Deleting " + ASSETS_PATH)
    shutil.rmtree(ASSETS_PATH)
    os.remove(ZIP_FILE)


def build_all(static_dist_root="frontend/static/dist", remove_existing=False):
    if remove_existing:
        relative_dist_root = "./" + static_dist_root
        if os.path.exists(relative_dist_root):
            shutil.rmtree(relative_dist_root)
    build_govuk_assets(static_dist_root=static_dist_root)
    static_assets.build_bundles(static_folder=static_dist_root)


if __name__ == "__main__":
    build_all(remove_existing=True)
