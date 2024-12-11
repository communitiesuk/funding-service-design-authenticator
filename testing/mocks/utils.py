"""
Utility functions for running tests and generating reports
"""

import os


def get_service_html_filepath(root_dir: str, route_rel: str):
    path = [root_dir]

    route_list = route_rel.split("/")
    filename = route_list.pop(len(route_list) - 1)
    if not filename:
        filename = "index"
    filename = filename + ".html"

    if len(route_list) > 0:
        cleaned_route_list = list(filter(lambda a: a != "", route_list))
        path.extend(cleaned_route_list)

    basename = os.path.join(*path) + os.path.sep

    return basename, filename


def print_html_page(html: str, route_rel: str):
    """
    Prints an html page to local dir
    """
    html_basename, filename = get_service_html_filepath("html", route_rel)

    os.makedirs(html_basename, exist_ok=True)
    f = open(html_basename + filename, "w")
    f.write(html)
    f.close()
