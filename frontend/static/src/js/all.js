AuthenticatorFrontend.initAll = function (options) {
  // Set the options to an empty object by default if no options are passed.
  options = typeof options !== 'undefined' ? options : {};

  // Allow Authenticator Frontend to be initialised in only certain sections of the page
  // Defaults to the entire document if nothing is set.
  let scope = typeof options.scope !== 'undefined' ? options.scope : document;

  let collapsibleDetails = scope.querySelectorAll(".govuk-details");
  AuthenticatorFrontend.nodeListForEach(collapsibleDetails, function (collapsible) {
    new AuthenticatorFrontend.Collapsible({
      collapsible: collapsible
    });
  });
}
