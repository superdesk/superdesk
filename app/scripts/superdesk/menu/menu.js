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

        .directive('sdMenuWrapper', ['superdesk', '$location', 'betaService',
        function(superdesk, $location, betaService) {
            return {
                require: '^sdSuperdeskView',
                templateUrl: require.toUrl('./views/menu.html'),
                link: function(scope, elem, attrs, ctrl) {

                    scope.flags = ctrl.flags;
                    scope.menu = _.values(_.where(superdesk.activities, {category: superdesk.MENU_MAIN}));

                    scope.selected = null;

                    scope.toggleMenu = function() {
                        ctrl.flags.menu = !ctrl.flags.menu;
                    };

                    scope.toggleNotifications = function() {
                        ctrl.flags.notifications = !ctrl.flags.notifications;
                    };

                    scope.toggleBeta = function() {
                        betaService.toggleBeta();
                    };

                    scope.$on('$routeChangeSuccess', function(ev, route) {
                        scope.currentRoute = route;
                        ctrl.flags.menu = false;
                        scope.selected = _.find(scope.menu, function(item) {
                            return $location.path().substr(0, item.href.length) === item.href;
                        });
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
