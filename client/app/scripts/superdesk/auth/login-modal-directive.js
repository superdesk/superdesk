define([], function() {
    'use strict';

    /**
     * Login modal is watching session token and displays modal when needed
     */
    LoginModalDirective.$inject = ['session', 'auth', 'features', 'asset', '$route'];
    function LoginModalDirective(session, auth, features, asset, $route) {
        return {
            replace: true,
            templateUrl: asset.templateUrl('superdesk/auth/login-modal.html'),
            link: function(scope, element, attrs) {

                scope.features = features;

                scope.authenticate = function() {
                    scope.isLoading = true;
                    scope.loginError = null;
                    auth.login(scope.username || '', scope.password || '')
                        .then(function() {
                            scope.isLoading = false;
                            scope.password = null;
                            if ($route.current.redirectTo) {
                                $route.reload();
                            }
                        }, function(rejection) {
                            scope.isLoading = false;
                            scope.loginError = rejection.status;
                            if (scope.loginError === 401) {
                                scope.password = null;
                            }
                        });
                };

                scope.$watchGroup([function getSessionToken() {
                    return session.token;
                }, 'requiredLogin'], function showLogin(triggerLogin) {
                    scope.isLoading = false;
                    scope.identity = session.identity;
                    scope.sessionId = session.sessionId;
                    scope.username = session.identity ? session.identity.UserName : null;
                    scope.password = null;
                    if (!triggerLogin[0] && triggerLogin[1] === true) {
                        scope.active = true;
                        var focusElem = scope.username ? 'password' : 'username';
                        element.find('#login-' + focusElem).focus();
                    } else {
                        scope.active = false;
                    }
                });
            }
        };
    }

    return LoginModalDirective;
});
