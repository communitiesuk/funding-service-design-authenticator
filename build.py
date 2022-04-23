import glob
import os
import shutil
import urllib.request
import zipfile
from swagger_ui_bundle import swagger_ui_3_52_0_path


def build_swagger():

    DIST_ROOT = "./swagger/dist/"
    SWAGGER_MODS_DIR = "./swagger/custom/3_52_0/"
    SWAGGER_BUNDLE_DIR = swagger_ui_3_52_0_path + "/"

    # # Checks if swagger has already built
    # if os.path.exists(DIST_ROOT):
    #     print(
    #         "Swagger already built."
    #         "If you require a rebuild manually run build.build_swagger"
    #     )
    #     return True

    # Attempts to delete the old files, states if
    # one doesn't exist.

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
        shutil.copy("".join([SWAGGER_MODS_DIR, file_to_copy]), "".join([DIST_ROOT, file_to_copy]))


if __name__ == "__main__":

    build_swagger()
