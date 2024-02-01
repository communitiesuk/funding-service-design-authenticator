# Funding Service Design - Authenticator

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![Funding Service Design Authenticator Deploy](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/deploy.yml/badge.svg)
[![CodeQL](https://github.com/communitiesuk/funding-service-design-authenticator/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-autheticator/actions/workflows/codeql-analysis.yml)

This is the authenticator repository for funding service design microservices. This service provides an API and associated model implementation required for authentication of frontend, assessment and other FSD services.

[Developer setup guide](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-setup.md)

This service depends on:
- A redis instance for storing magic links
- [fund-store](https://github.com/communitiesuk/funding-service-design-fund-store)
- [account-store](https://github.com/communitiesuk/funding-service-design-account-store)
- [notification](https://github.com/communitiesuk/funding-service-design-notification)

## Overview

If you want an overview of how this service functions including architecture and features there's a fuller description in the [/docs/README here](/docs/README.md).


# Translations

This repo uses pybable for translation. Useful commands contained in [tasks.py](./taskspy), more detail available [here](https://dluhcdigital.atlassian.net/wiki/spaces/FS/pages/79174033/How+to+update+Welsh+translations+in+Access+Funding)


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
- `AUTHENTICATOR_HOST`
- `ACCOUNT_STORE_API_HOST`
- `APPLICATION_STORE_API_HOST`
- `NOTIFICATION_SERVICE_HOST`
- `APPLICANT_FRONTEND_HOST`
- `ASSESSMENT_FRONTEND_HOST`
- `FUND_STORE_API_HOST`
- `RSA256_PUBLIC_KEY_BASE64`
- `RSA256_PRIVATE_KEY_BASE64`
- `AZURE_AD_CLIENT_ID`
- `AZURE_AD_CLIENT_SECRET`
- `AZURE_AD_TENANT_ID`
- `SECRET_KEY`
- `COOKIE_DOMAIN`
- `SENTRY_DSN`
- `GITHUB_SHA`
- `ALLOW_ASSESSMENT_LOGIN_VIA_MAGIC_LINK`
- `POST_AWARD_FRONTEND_HOST`
## Copilot
Copilot is used for infrastructure deployment. Instructions are available [here](https://github.com/communitiesuk/funding-service-design-workflows/blob/main/readmes/python-repos-copilot.md), with the following values for the authenticator:
- service-name: fsd-authenticator
- image-name: funding-service-design-authenticator

# Pull Requests
Authenticator has a different set of requirements for PR reviewers, as it is relied upon by multiple services (pre-award and post-award). It requires a minimum of 2 reviewers to approve a PR before merge, and will auto-request a review from the following 2 teams when a PR is raised:
- fsd-post-award-deployers
- fsd-pre-award-deployers
These teams are configured in the [CODEOWNERS](./.github/CODEOWNERS) file.
Github cannot enforce the 2 reviews coming from 2 different teams, so please make sure you have 2 appropriate reviews before merging.
