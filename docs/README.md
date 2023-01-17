# Getting started with Authenticator

## A Combined Repo
Most repos in the Funding Service Design architecture are either backend *stores* or UI *frontends*. Authenticator is different in that it incorporates both frontend and backend responsibilities in the same place.

It does not operate as a data store, however it does use a **redis** instance for temporary storage of session and access related info.

The long term persistent storage of user data is handled instead by the FSD account-store, and DLUHC Azure Active Directory (AD) Single Sign-on (SSO) tenant.

The original reason for combining the two was that the frontend views are mostly just human-readable error messages or user prompts for the backend api endpoints.
## Frontend and Backend Directories
### Frontend
The code for the frontend views and endpoints are in the [`/frontend`](/frontend) directory. These include things like error messages, user authentication state displays and user email input pages.

### Backend
The code for the backend endpoints are stored in the [`/api`](/api) directory. These include things like SSO login redirects and *magic-link* endpoints

## Other directories

- [`/models`](/models) - the shared models for the service (including models and lookups for objects on other services)
- [`/security`](/security) - security utils used by both front and backend
- [`/openapi`](/openapi) - the OpenApi config for the backend routes at [`/api`](/api)
- [`/config`](/config) - the environment config files
- [`/swagger`](/swagger) - the customised components of swagger (used by [`build.py`](/build.py) to build a customised version of swagger without the default search bar at the top)
- [`/.github`](/.github) - GitHub deployment workflow files
- [`/run`](/run) - Gunicorn worker config scripts for dev/test environments
- [`/tests`](/tests) - tests
- [`/docs`](/docs) - these docs

## JWT Auth Principles
### How it works
This service issues *signed* tokens, like a digital ticket, which is saved in a user's browser as cookie. The token contains *claims* about the user (like their name, email and account id), and a hash of that data which is signed using the private key of an RSA256 key pair.

When this token is saved in a cookie by this authenticator, with both this authenticator and the other microservices on a common domain like `.access-funding.levellingup.gov.uk` it can then be read by any other microservices.

Those services can check the *signature* on the token using the public key from the RSA256 keypair to verify that the data in it has been issued by this authenticator service.

For this to work, an RSA256 public/private key pair needs to be created, with at least the private key being available in this authenticator's environment as an env var to sign the token, and on any service that needs to be able to verify the signature, the public key of the pair needs to be available as a var to verify the signature.

The benefit of this shared keypair with token approach is that the other services do not need to make a call to a central service to see if the current user is authenticated, they just need to check the signature is valid (and that it is not out of expired) to confirm that the user is who they say they are.

We set an expiry time on the token to set the time after which the other services should consider the token invalid, and redirect the user back to this authenticator service to revalidate their ID and get issued with fresh token.

### Where we use it
We set our auth JWT cookie, start the user's session and redirect to their chosen service in one step in [AuthSessionView.create_session_and_redirect](/api/session/auth_session.py#L99).

The method that creates the token itself (and where you can see the claims we are adding to the token payload) is [AuthSessionView.create_session_details_with_token](/api/session/auth_session.py#L137)

The name for the user token cookie is set by the config variable `FSD_USER_TOKEN_COOKIE_NAME` which is currently set in the [default.py](/config/envs/default.py) config file as "*fsd_user_token*".

When you use either magic link or SSO method to log in (described below), you should see the token cookie in Chrome developer tools, in the Application tab, if you select Storage>Cookies in the Application tab sidebar, and then select your current host name in the drop-down. In the list of cookies, find the one called "fsd_user_token" and then you can see the encoded (but not encrypted) value. If you select and copy the value there, and then go to [jwt.io](https://jwt.io) and paste it into the "encoded" left panel you can then see what the decoded JWT contains (and the payload of claims that have been set).

## Magic Links
### What are magic links?
"Magic links" are the friendly name sometimes given to single-use-links that have the effect of authenticating a user, or performing some other one-time action.

### How do we use them?
In this application we use one time links to authenticate applicants using the applicant frontend instead of them having to use passwords.

Applicants are directed to visit the [`/service/magic-links/new`](/frontend/magic_links/routes.py#L79) route on this service where they can enter an email address and click a button to request a magic link.

The service creates a unique link reference and stores this reference in the `redis` key/value store together with data about the email address requested and how long this link should last until it expires (eg. 24hrs), and then sends a notification with a link which contains this reference to the email account, using the FSD notification service (which sends the email via Gov Notify).

The user is then redirected to the [`/service/magic-links/check-email`](/frontend/magic_links/routes.py#L121) route which confirms to the user that a magic link email has been sent to their address and they should check their inbox. 

The user clicks the link in the email which links to the [`/service/magic-links/landing/<link_id>`](/frontend/magic_links/routes.py#L49) route which displays a 'continue' button. 

NOTE: This landing page exists to prevent email software bots from prematurely following and "using" the one-time link before the user has opened the email and followed it themselves. (Mail software bots sometimes "click" links in client's emails to check for malicious code before displaying them to the user)

When the user clicks the "continue" button on the landing view, they are redirected to the actual magic-link endpoint on the backend api at [`/magic-links/<link_id>`](/api/magic_links/routes.py#L22) which "claims" the magic link, checks it is valid, redirects the user to the applicant frontend, and deletes the magic link record from the store so that it cannot be used again.

### Redis storage of link references
The *redis* key/value store is like a very simple, flat data store, it is just a dictionary of key/value pairs. There are no tables or columns to relate data objects.

However sometimes you want to store bits of data in different ways so that it's quick and easy to look up.

In this application, as well as storing the magic-link "key" (a short string of characters) with a value of a data object (which includes the user's email and magic link expiry time), we also want to ensure that each user only has one active magic link at any one time.

To achieve this, as well as storing the magic link key, we also store a user account key with a value of the magic link key.

So when a user requests a new magic link, we first check if they have an existing account key in the *redis* instance. If they do, we remove the link key referenced by the old account key, create a new magic link (and key) and then update the account key value with the new link key. This has the effect of deleting the old magic link and replacing it with the new one.

To enable two namespaces of keys like this, *redis* has a concept of *prefixes* so in this application, we use the prefix of [`link:`](/models/magic_link.py#L196) on keys that reference links, and the prefix of [`account:`](/models/magic_link.py#L173) on keys that reference accounts.

## SSO / Azure AD

### What is single sign-on (SSO)
SSO is what happens when you "Sign in using Google" or "Sign in using Facebook". In these cases an Identity Provider (IDP) takes responsibility for verifying the user's identity (eg. getting them to log in with a password, and verify by a text to their phone). The IDP then lets the service securely know that the user has signed in successfully and then passes the session back to the service that wants to authenticate the user.

### What is Azure AD (AD or AAD)
Azure AD is an IDP provided by Microsoft, that let's organisations manage their own directory of user accounts.

### How do we use it?
This service uses Azure AD via an integration using the [`msal`](https://pypi.org/project/msal/) (Microsoft Authentication Library) package provided by Microsoft.

We have exposed a number of endpoints on this services backend api, eg. [`/sso/login`](/api/sso/routes.py#L17), [`/sso/logout`](/api/sso/routes.py#L28), [`/sso/get-token`](/api/sso/routes.py#L55) which use redirects and background calls (mostly handled for us by the *msal* package) which are used to log the user in and out.

### Logging in with SSO
When a user visits the [`/sso/login`](/api/sso/routes.py#L17) endpoint, they are redirected to Microsoft Azure to login, once logged in, Azure redirects the user back to [`/sso/get-token`](/api/sso/routes.py#L55) with a code in the querystring.

The *msal* package configured at that endpoint takes the code from the querystring and makes a background callback to redeem that code and allow Azure to confirm that it has issued the code and the user has indeed just logged in successfully on their side.

Azure then sends a signed token back which contains the authenticated user's ID claims (their email address, azure subject id and and roles they have associated with their account for example).

If we receive a successful response back from Microsoft at [`/sso/get-token`](/api/sso/routes.py#L55) then we consider the user authenticated and we issue them with a signed token cookie (see above) which allows them to access our other services (appropriate to their roles).

### Role management
Different users on the service have different roles that allow them to different things.

User's roles are stored in the account store via the account>role related object. Every time a user logs in via SSO, the roles that the user has are sent in the claims payload from Azure AD, and these are updated to the user's account record, and then set on the token cookie, so wherever the cookie is read, the user's roles can also be read.

The role types are created in Azure AD, and assigned to groups. Users can be made members of the appropriate group in Azure AD (eg. "Commenters"), the user will then inherit the roles of the group.

### Who needs what roles?
*Applicants* do not require any roles at all currently nor do they need to use Azure AD to sign in (they can just use a magic link).

Those using the *Assessment* frontend must be registered on the DLUHC FSD Azure AD tenant and also must have at least the role of "COMMENTER" (i.e. be in the "Commenters" group on Azure AD).

### Permission denied error messages
If an applicant user tried to access the assessment frontend (for assessment processes) they would be redirected to the [`/service/user`](/frontend/user/routes.py#L18) endpoint with a `?roles_required=COMMENTER` query string argument.

The [`/service/user`](/frontend/user/routes.py#L18) endpoint shows confirmation of the account email of the current logged in user. However if the user has tried to access an area that they do not have appropriate roles for, they will be redirected to the [`/service/user`](/frontend/user/routes.py#L18)  endpoint with redirect with the *roles_required=...* argument appended this will then display to the user a 403 permission denied error message.

## [fsd_utils](https://pypi.org/project/funding-service-design-utils/)
The [funding-service-design-utils](https://pypi.org/project/funding-service-design-utils/) package on pypi also has an [authentication toolkit](https://github.com/communitiesuk/funding-service-design-utils/blob/main/fsd_utils/authentication/) that goes with this service.

The *fsd_utils* package should be installed on services in this system that need to authenticate users with the JWT issued by this authenticator service.

It includes [some handy decorators](https://github.com/communitiesuk/funding-service-design-utils/blob/main/fsd_utils/authentication/decorators.py):

### `@login_required`
If this is added to a flask route, it will require the user to have a valid JWT to access the route. If not, the user will be redirected to the [`/session/sign-out` (clear_session)](/api/session/auth_session.py#L49) backend endpoint on this service.

If the user has a valid JWT auth cookie, a number of attributes will be set on the flask `g` global request object. Properties that will be set include `g.is_authenticated=True`, and `g.user` will be set with a User object containing properties such as `g.user.email`, `g.user.full_name`, `g.user.roles` (a list of roles that the user has) and `g.user.highest_role` which is a string value of the users highest role in the roles hierarchy.

It will also set a `g.logout_url` variable which (at the time of writing) is set to [`/sessions/signout`](/openapi/api.yml#L136) - NOTE: this sign out endpoint is designed primarily for magic-link users as it just deletes the JWT cookie from the user's browser. SSO authenticated users should use the [`/sso/logout`](/openapi/api.yml#L94) endpoint to logout fully via Azure AD.

The `@login_required` decorator also takes an optional `roles_required` argument. This can be set to a list of roles that a user must have in order to access the route. If the user is authenticated but does not have the required roles, they will be redirected to the [`/service/user?roles_required=...`](/frontend/user/routes.py#L18) endpoint on this service with the *roles_required* value representing a list of required roles as set on the decorator.

### `@login_requested`
If this is added to a flask route, it will check if the user has a valid JWT and update the flask `g` variables as above. But if the user cannot be authenticated this decorator will still let the request continue to the route.

This should be used where a route (eg. a landing page) can be accessed by both un-authenticated and authenticated users and the logic just needs to display different views to different user states.
