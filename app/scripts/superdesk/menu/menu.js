define(['angular', 'require', 'lodash'], function(angular, require, _) {
    'use strict';

    return angular.module('superdesk.menu', [])

        // set flags for other directives
        .directive('sdSuperdeskView', function() {
            return {
                templateUrl: require.toUrl('./views/superdesk-view.html'),
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
        })

        .directive('sdMenuWrapper', ['superdesk', '$route', 'betaService',
        function(superdesk, $route, betaService) {
            return {
                require: '^sdSuperdeskView',
                templateUrl: require.toUrl('./views/menu.html'),
                link: function(scope, elem, attrs, ctrl) {

                    scope.currentRoute = $route.current;
                    scope.flags = ctrl.flags;
                    scope.menu = _.values(_.where(superdesk.activities, {category: superdesk.MENU_MAIN}));
                    findActive();

                    scope.toggleMenu = function() {
                        ctrl.flags.menu = !ctrl.flags.menu;
                    };

                    scope.toggleNotifications = function() {
                        ctrl.flags.notifications = !ctrl.flags.notifications;
                    };

                    scope.toggleBeta = function() {
                        betaService.toggleBeta();
                    };

                    function findActive() {
                        _.each(scope.menu, function(activity) {
                            activity.isActive = scope.currentRoute.href.substr(0, activity.href.length) === activity.href;
                        });
                    }

                    scope.$on('$locationChangeStart', function() {
                        ctrl.flags.menu = false;
                    });

                    scope.$on('$routeChangeSuccess', function() {
                        scope.currentRoute = $route.current;
                        findActive();
                    });
                }
            };
        }])

        .directive('sdNotifications', function() {
            return {
                require: '^sdSuperdeskView',
                templateUrl: require.toUrl('./views/notifications.html'),
                link: function(scope, elem, attrs, ctrl) {
                    scope.flags = ctrl.flags;
                }
            };
        });
});
