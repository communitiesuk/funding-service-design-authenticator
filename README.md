# Funding Service Design - Authenticator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![Funding Service Design Authenticator Deploy](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/deploy.yml/badge.svg)
[![CodeQL](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-autheticator/actions/workflows/codeql-analysis.yml)

Repo for the DLUCH Funding Service Design Authenticator.

Built with Flask.

## Prerequisites
- python ^= 3.10
- redis ^= 7.0.0

# Getting started

## Installation

- Clone the repository
- Ensure you have [Redis](https://redis.io/docs/getting-started/) installed and running, with a clean instance available at *redis://localhost:6379*

### Create a Virtual environment

    python3 -m venv .venv

### Enter the virtual environment

...either macOS using bash:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

### Install dependencies
From the top-level directory enter the command to install pip and the dependencies of the project

    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

NOTE: requirements-dev.txt and requirements.txt are updated using [pip-tools pip-compile](https://github.com/jazzband/pip-tools)
To update requirements please manually add the dependencies in the .in files (not the requirements.txt files)
Then run:

    pip-compile requirements.in

    pip-compile requirements-dev.in

## How to use
Enter the virtual environment as described above, then:

### Build Swagger & GovUK Assets

This build step imports assets required for the GovUK template and styling components.
It also builds customised swagger files which slightly clean the layout provided by the vanilla SwaggerUI 3.52.0 (which is included in dependency swagger-ui-bundle==0.0.9) are located at /swagger/custom/3_52_0.

Before first usage, the vanilla bundle needs to be imported and overwritten with the modified files. To do this run:

    python3 build.py

Developer note: If you receive a certification error when running the above command on macOS,
consider if you need to run the Python
'Install Certificates.command' which is a file located in your globally installed Python directory. For more info see [StackOverflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate)

### Run Flask

Run:

    flask run

A local dev server will be created on

    http://localhost:5000

Flask environment variables are configurable in `.flaskenv`

# Run with Gunicorn

In deployed environments the service is run with gunicorn. You can run the service locally with gunicorn to test

First set the FLASK_ENV environment you wish to test eg:

    export FLASK_ENV=dev

Then run gunicorn using the following command:

    gunicorn wsgi:app -c run/gunicorn/local.py

# Configuration

# Pipelines

These are the current pipelines running on the repo:

* Deploy to Gov PaaS - This is a simple pipeline to demonstrate capabilities.  Builds, tests and deploys a simple python application to the PaaS for evaluation in Dev and Test Only.
* NOTE: THIS IS A CUSTOM DEPLOY WORKFLOW AND DOES NOT YET USE THE WORKFLOW TEMPLATE FOR FUNDING SERVICE DESIGN PENDING UPDATE

# Testing

## Unit & Accessibility Testing

To run all tests run:

    pytest

## Performance Testing

Performance tests are stored in a separate repository which is then run in the pipeline. If you want to run the performance tests yourself follow the steps in the README for the performance test repo located [here](https://github.com/communitiesuk/funding-service-design-performance-tests/blob/main/README.md)


# Extras

This repo comes with a .pre-commit-config.yaml, if you wish to use this do
the following while in your virtual enviroment:

    pre-commit install

Once the above is done you will have autoformatting and pep8 compliance built
into your workflow. You will be notified of any pep8 errors during commits.
