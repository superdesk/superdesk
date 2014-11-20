(function() {
    'use strict';

    angular.module('superdesk.menu', ['superdesk.menu.notifications', 'superdesk.asset'])

        // set flags for other directives
        .directive('sdSuperdeskView', ['asset', function(asset) {
            return {
                templateUrl: asset.templateUrl('superdesk/menu/views/superdesk-view.html'),
                controller: function() {
                    this.flags = {
                        menu: false,
                        notifications: false
                    };
                },
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        }])

        .directive('sdMenuWrapper', ['$route', 'superdesk', 'betaService', 'userNotifications', 'asset',
        function($route, superdesk, betaService, userNotifications, asset) {
            return {
                require: '^sdSuperdeskView',
                templateUrl: asset.templateUrl('superdesk/menu/views/menu.html'),
                link: function(scope, elem, attrs, ctrl) {

                    scope.currentRoute = null;
                    scope.flags = ctrl.flags;
                    scope.menu = [];

                    superdesk.getMenu(superdesk.MENU_MAIN).then(function(menu) {
                        scope.menu = menu;
                        setActiveMenuItem($route.current);
                    });

                    scope.toggleMenu = function() {
                        ctrl.flags.menu = !ctrl.flags.menu;
                    };

                    scope.toggleNotifications = function() {
                        ctrl.flags.notifications = !ctrl.flags.notifications;
                    };

                    scope.toggleBeta = function() {
                        betaService.toggleBeta();
                    };

                    function setActiveMenuItem(route) {
                        _.each(scope.menu, function(activity) {
                            activity.isActive = route && route.href &&
                                route.href.substr(0, activity.href.length) === activity.href;
                        });
                    }

                    scope.$on('$locationChangeStart', function() {
                        ctrl.flags.menu = false;
                    });

                    scope.$watch(function currentRoute() {
                        return $route.current;
                    }, function(route) {
                        scope.currentRoute = route || null;
                        setActiveMenuItem(scope.currentRoute);
                    });

                    scope.notifications = userNotifications;
                }
            };
        }]);
})();
