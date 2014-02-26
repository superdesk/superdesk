define([], function() {
    'use strict';

    LoginModalDirective.$inject = ['auth'];
    function LoginModalDirective(auth) {
        return {
            restrict: 'A',
            replace: true,
            templateUrl: 'scripts/superdesk/auth/login-modal.html',
            link: function(scope, element, attrs) {

                scope.isLoading = false;
                scope.onlypassword = false;

                scope.different = function() {
                    scope.onlypassword = false;
                };

                if (!auth.identity) {
                    scope.onlypassword = false;
                    element.show();
                }

                scope.authenticate = function() {
                    scope.isLoading = true;
                    auth.login(scope.username, scope.password, scope.rememberMe)
                        .then(function() {
                            scope.isLoading = false;
                            scope.password = null;
                            scope.loginError = false;
                            element.hide();
                        }, function() {
                            scope.isLoading = false;
                            scope.password = null;
                            scope.loginError = true;
                            element.show();
                        });
                };

                scope.$watch(function() {
                    return auth.identity;
                }, function(identity) {
                    if (identity == null) {
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
