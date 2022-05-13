"""Compile static assets."""
from flask_assets import Bundle


def compile_static_assets(assets, build=True):
    """Configure and build asset bundles."""

    # Main asset bundles
    # Paths are relative to Flask static_folder
    # Requires:
    # - pyScss>=1.4.0
    # - cssmin==0.2.0
    default_style_bundle = Bundle(
        "../src/scss/*.scss",
        filters="pyscss,cssmin",
        output="css/main.min.css",
        extra={"rel": "stylesheet/css"},
    )

    # Requires:
    # - jsmin==3.0.1
    default_js_bundle = Bundle(
        "../src/js/*.js",
        filters="jsmin",
        output="js/main.min.js",
    )

    assets.register("default_styles", default_style_bundle)
    assets.register("main_js", default_js_bundle)
    if build:
        default_style_bundle.build()
        default_js_bundle.build()
