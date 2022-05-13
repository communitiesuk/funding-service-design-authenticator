import glob
import os
import shutil
import urllib.request
import zipfile

from config.environments.default import Config
from swagger_ui_bundle import swagger_ui_3_52_0_path


def build_govuk_assets():

    # NOTE: When using connexion for our openapi management
    # FLASK_STATIC_URL needs to be "/static"
    # as static_url_path is not directly configurable
    # with the connexion app constructor connexion.FlaskApp()
    # so the default /static url needs to be used
    FLASK_STATIC_URL = "/" + Config.STATIC_FOLDER
    DIST_ROOT = "./frontend/static/dist"
    GOVUK_DIR = "/govuk-frontend"
    GOVUK_URL = (
        "https://github.com/alphagov/govuk-frontend/"
        "releases/download/v4.0.0/release-v4.0.0.zip"
    )
    ZIP_FILE = "./govuk_frontend.zip"
    DIST_PATH = DIST_ROOT + GOVUK_DIR
    ASSETS_DIR = "/assets"
    ASSETS_PATH = DIST_PATH + ASSETS_DIR

    # Checks if GovUK Frontend Assets already built
    if os.path.exists(DIST_PATH):
        print(
            "GovUK Frontend assets already built."
            "If you require a rebuild manually run build.build_govuk_assets"
        )
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

    # Update relative paths

    print("Updating relative paths in css files to " + GOVUK_DIR)
    cwd = os.getcwd()
    os.chdir(DIST_PATH)
    for css_file in glob.glob("*.css"):

        # Read in the file
        with open(css_file, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace(ASSETS_DIR, FLASK_STATIC_URL + GOVUK_DIR)

        # Write the file out again
        with open(css_file, "w") as file:
            file.write(filedata)
    os.chdir(cwd)

    # Delete temp files
    print("Deleting " + ASSETS_PATH)
    shutil.rmtree(ASSETS_PATH)
    os.remove(ZIP_FILE)


def build_swagger():

    DIST_ROOT = "./swagger/dist/"
    SWAGGER_MODS_DIR = "./swagger/custom/3_52_0/"
    SWAGGER_BUNDLE_DIR = swagger_ui_3_52_0_path + "/"

    print("Deleting old " + DIST_ROOT)
    try:
        shutil.rmtree(DIST_ROOT)
    except FileNotFoundError:
        print("No old " + DIST_ROOT + " to remove.")

    print("Making dir " + DIST_ROOT + "")
    os.mkdir(os.path.dirname(DIST_ROOT))

    # Move files from SWAGGER_BUNDLE_DIR to DIST_PATH

    print("Copying files from " + SWAGGER_BUNDLE_DIR + " to " + DIST_ROOT)
    for file_to_copy in os.listdir(SWAGGER_BUNDLE_DIR):
        shutil.copy("".join([SWAGGER_BUNDLE_DIR, file_to_copy]), DIST_ROOT)

    # Copy custom files from SWAGGER_MODS_DIR to DIST_PATH

    print("Copying files from " + SWAGGER_MODS_DIR + " to " + DIST_ROOT)
    for file_to_copy in os.listdir(SWAGGER_MODS_DIR):
        print("Copying " + file_to_copy)
        shutil.copy(
            "".join([SWAGGER_MODS_DIR, file_to_copy]),
            "".join([DIST_ROOT, file_to_copy]),
        )


if __name__ == "__main__":

    build_swagger()
    build_govuk_assets()
