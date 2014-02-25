define([], function() {
    'use strict';

    var LoginModalDirective = function(auth) {
        return {
            restrict: 'A',
            replace: true,
            templateUrl: 'scripts/superdesk/auth/login-modal.html',
            link: function(scope, element, attrs) {

                scope.onlypassword = true;

                scope.different = function() {
                    scope.onlypassword = false;
                    //other code
                };

                if (!auth.identity) {
                    element.show();
                }

                scope.authenticate = function() {
                    scope.loading = true;
                    auth.login(scope.username, scope.password, scope.rememberMe)
                        .then(function() {
                            delete scope.loading;
                            scope.password = null;
                            scope.loginError = false;
                            element.hide();
                        }, function() {
                            delete scope.loading;
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
    };

    LoginModalDirective.$inject = ['auth'];
    return LoginModalDirective;
});
