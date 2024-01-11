# Funding Service Design - Authenticator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![Funding Service Design Authenticator Deploy](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/deploy.yml/badge.svg)
[![CodeQL](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-autheticator/actions/workflows/codeql-analysis.yml)

This is the authenticator for funding service design Access Funding and Assessment. This service provides an API and associated model implementation required for authentication of frontend and assessment.

[Developer setup guide](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-setup.md)

This service depends on:
- A redis instance
- [fund-store](https://github.com/communitiesuk/funding-service-design-fund-store)
- [account-store](https://github.com/communitiesuk/funding-service-design-account-store)
- [notification](https://github.com/communitiesuk/funding-service-design-notification)

## Overview

If you want an overview of how this service functions including architecture and features there's a fuller description in the [/docs/README here](/docs/README.md).


# Translations

Updating translations:

    pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .
    pybabel update -i messages.pot -d frontend/translations
    pybabel compile -d frontend/translations


# Testing
[Testing in Python repos](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-db-development.md)


# IDE Setup
[Python IDE Setup](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-ide-setup.md)


# Builds and Deploys
Details on how our pipelines work and the release process is available [here](https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/73695505/How+do+we+deploy+our+code+to+prod)
## Paketo
Paketo is used to build the docker image which gets deployed to our test and production environments. Details available [here](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-paketo.md)

For Authenticator,
`envs` needs to include values for each of:
AUTHENTICATOR_HOST
ACCOUNT_STORE_API_HOST
APPLICATION_STORE_API_HOST
NOTIFICATION_SERVICE_HOST
APPLICANT_FRONTEND_HOST
ASSESSMENT_FRONTEND_HOST
FUND_STORE_API_HOST
RSA256_PUBLIC_KEY_BASE64
RSA256_PRIVATE_KEY_BASE64
AZURE_AD_CLIENT_ID
AZURE_AD_CLIENT_SECRET
AZURE_AD_TENANT_ID
SECRET_KEY
COOKIE_DOMAIN
SENTRY_DSN
GITHUB_SHA
ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK
POST_AWARD_FRONTEND_HOST
## Copilot
Copilot is used for infrastructure deployment. Instructions are available [here](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-copilot.md), with the following values for the fund store:
- service-name: fsd-authenticator
- image-name: funding-service-design-authenticator
