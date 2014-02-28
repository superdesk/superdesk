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
                    auth.login(scope.username, scope.password)
                        .then(function() {
                            scope.isLoading = false;
                            scope.password = null;
                            scope.loginError = false;
                        }, function() {
                            scope.isLoading = false;
                            scope.password = null;
                            scope.loginError = true;
                        });
                };

                scope.$watch(function() {
                    return session.token;
                }, function(token) {
                    scope.isLoading = false;
                    scope.identity = session.identity;
                    scope.username = session.identity ? session.identity.UserName : null;
                    if (!token) {
                        element.show();
                        element.find('#username').focus();
                    } else {
                        element.hide();
                    }
                });
            }
        };
    }

    return LoginModalDirective;
});
