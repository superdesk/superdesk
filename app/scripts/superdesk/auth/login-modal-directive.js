define([], function() {
    'use strict';

    var LoginModalDirective = function(auth) {
        return {
            restrict: 'A',
            replace: true,
            templateUrl: 'scripts/superdesk/auth/login-modal.html',
            link: function(scope, element, attrs) {

                element.modal({
                    keyboard: false,
                    show: !auth.identity
                });

                scope.authenticate = function() {
                    scope.loading = true;
                    auth.login(scope.username, scope.password, scope.rememberMe)
                        .then(function() {
                            delete scope.loading;
                            scope.password = null;
                            scope.loginError = false;
                            element.modal('hide');
                        }, function() {
                            delete scope.loading;
                            scope.password = null;
                            scope.loginError = true;
                            element.modal('show');
                        });
                };

                scope.$watch(function() {
                    return auth.identity;
                }, function(identity) {
                    if (identity == null) {
                        element.modal('show');
                        element.find('#username').focus();
                    } else {
                        element.modal('hide');
                    }
                });
            }
        };
    };

    LoginModalDirective.$inject = ['auth'];
    return LoginModalDirective;
});
