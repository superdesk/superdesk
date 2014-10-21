define([], function() {
    'use strict';

    /**
     * Login modal is watching session token and displays modal when needed
     */
    LoginModalDirective.$inject = ['session', 'auth'];
    function LoginModalDirective(session, auth) {
        return {
            replace: true,
            templateUrl: 'scripts/superdesk/auth/login-modal.html',
            link: function(scope, element, attrs) {

                scope.authenticate = function() {
                    scope.isLoading = true;
                    scope.loginError = null;
                    auth.login(scope.username || '', scope.password || '')
                        .then(function() {
                            scope.isLoading = false;
                            scope.password = null;
                        }, function(rejection) {
                            scope.isLoading = false;
                            scope.loginError = rejection.status;
                            if (scope.loginError === 400) {
                                scope.password = null;
                            }
                        });
                };

                scope.$watchGroup([function() {
                    return session.token;
                }, 'requiredLogin'], function(triggerLogin) {
                    scope.isLoading = false;
                    scope.identity = session.identity;
                    scope.sessionId = session.sessionId;
                    scope.username = session.identity ? session.identity.UserName : null;
                    scope.password = null;
                    if (!triggerLogin[0] && triggerLogin[1]) {
                        element.show();
                        var focusElem = scope.username ? 'password' : 'username';
                        element.find('#login-' + focusElem).focus();
                    } else {
                        element.hide();
                    }
                });
            }
        };
    }

    return LoginModalDirective;
});
