"""
Tests if selected pages of the website are accessible when rendered,
according to WCAG standards
"""
import os

import pytest
from axe_selenium_python import Axe
from flask import url_for
from json2html import json2html
from selenium.webdriver.chrome.webdriver import WebDriver
from tests.route_testing_conf import magic_link_routes_and_test_content
from tests.utils import get_service_html_filepath


def get_report_heading(route_rel: str):
    heading = "<h1>Axe Violations Report for route /" + route_rel + "</h1>"
    return heading


def get_report_filename(route_rel: str, route_name: str):

    if not route_name:
        if route_rel:
            route_name = route_rel.replace("/", "_")
        else:
            route_name = "index"

    return route_name


def print_axe_report(results: dict, route_rel: str):
    """
    Prints an html report from aXe generated results
    """
    results_html = json2html.convert(
        json=results["violations"],
        table_attributes=(
            "border='1' cellpadding='10' cellspacing='0' bordercolor='black'"
        ),
    )
    heading = get_report_heading(route_rel)
    results_with_title = heading + results_html
    html_basename, filename = get_service_html_filepath(
        "axe_reports", route_rel
    )

    os.makedirs(html_basename, exist_ok=True)
    f = open(html_basename + filename, "w")
    f.write(results_with_title)
    f.close()


@pytest.mark.usefixtures("selenium_chrome_driver")
def run_axe_and_print_report(
    driver: WebDriver,
    route_rel: str = "",
):
    """
    Generates an html report from aXe generate has generated a report
    :return A json report
    """
    if route_rel and route_rel[0] != "/":
        route_rel = "/" + route_rel
    route = url_for("default_bp.index", _external=True) + route_rel
    driver.get(route)
    axe = Axe(driver)
    axe.inject()
    results = axe.run()
    print_axe_report(results, route_rel)

    return results


@pytest.mark.app(debug=False)
def test_app(app):
    assert not app.debug, "Ensure the app not in debug mode"


@pytest.mark.usefixtures("selenium_chrome_driver")
class TestAccessibilityWithChrome:
    def test_homepage_accessible(self):
        """
        GIVEN Our Flask Application is running
        WHEN the '/' page (index) is requested (GET)
        THEN check that page returned conforms to WCAG standards
        """
        route_rel = ""
        results = run_axe_and_print_report(
            driver=self.driver, route_rel=str(route_rel)
        )
        assert len(results["violations"]) <= 2
        assert (
            len(results["violations"]) == 0
            or results["violations"][0]["impact"] == "moderate"
        )

    def test_magic_link_routes_accessible(self):
        """
        GIVEN Our Flask Application is running
        WHEN dictionary of known routes is requested (GET)
        THEN check that each page returned conforms to WCAG standards
        """
        for route_rel, _ in magic_link_routes_and_test_content.items():
            results = run_axe_and_print_report(
                driver=self.driver, route_rel=str(route_rel)
            )
            assert len(results["violations"]) <= 2
            assert (
                len(results["violations"]) == 0
                or results["violations"][0]["impact"] == "moderate"
            )

    def test_unknown_page_returns_accessible_404(self):
        """
        GIVEN Our Flask Application is running
        WHEN the '/page-that-does-not-exist' page is requested (GET)
        THEN check that a 404 page that is returned conforms to WCAG standards
        """
        route_rel = "page-does-not-exist"
        results = run_axe_and_print_report(
            driver=self.driver, route_rel=str(route_rel)
        )

        assert len(results["violations"]) <= 2
        assert (
            len(results["violations"]) == 0
            or results["violations"][0]["impact"] == "moderate"
        )
