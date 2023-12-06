const DEFAULT_CONSENT = {'analytics_storage': 'denied'}
const COOKIE_FSD_CONSENT = "fsd_cookie_consent";

function readConsentCookie() {
    const cookie = document.cookie.split(";").find(c => c.trim().startsWith(`${COOKIE_FSD_CONSENT}=`));
    return cookie ? JSON.parse(atob(cookie.split("=")[1])) : null;
}

function updateCookieConsent(value) {
    const consentObject = {'analytics_storage': value};
    gtag('consent', 'update', consentObject);
    document.cookie = `${COOKIE_FSD_CONSENT}=${btoa(JSON.stringify(consentObject))};path=` + "/";
}

function acceptCookies() {
    updateCookieConsent('granted');
    document.getElementById("cookies-choice-msg").setAttribute("hidden", "true");
    document.getElementById("cookies-accepted-msg").removeAttribute("hidden");
}

function denyCookies() {
    updateCookieConsent('denied');
    document.getElementById("cookies-choice-msg").setAttribute("hidden", "true");
    document.getElementById("cookies-rejected-msg").removeAttribute("hidden");
}

function hideCookiesMessage() {
    document.getElementById("cookie-banner").setAttribute("hidden", "true");
}

function unhideCookiesMessage() {
    document.getElementById("cookie-banner").removeAttribute("hidden");
}


function saveAnalyticsPrefs() {
    if (document.getElementById("cookies-analytics").checked) {
        updateCookieConsent('granted');
        hideCookiesMessage();
    } else {
        updateCookieConsent('denied');
        hideCookiesMessage();
    }
}