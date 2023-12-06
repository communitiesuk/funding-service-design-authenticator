AuthenticatorFrontend.initAll = function (options) {
  options = typeof options !== 'undefined' ? options : {};

  let scope = typeof options.scope !== 'undefined' ? options.scope : document;

  let collapsibleDetails = scope.querySelectorAll(".govuk-details");
  AuthenticatorFrontend.nodeListForEach(collapsibleDetails, function (collapsible) {
    new AuthenticatorFrontend.Collapsible({
      collapsible: collapsible
    });
  });
}
