define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    var module = angular.module('superdesk.directives');

    module.directive('sdMenuWrapper', ['$route', 'superdesk', '$location', function($route, superdesk, $location) {
        return {
            templateUrl: 'scripts/superdesk/views/sidebar-nav.html',
            link: function(scope, elem, attrs) {
                scope.menu = _.values(_.where(superdesk.activities, {category: superdesk.MENU_MAIN}));
                scope.displayMenu = false;

                scope.isActive = function(item) {
                    return $location.path().substr(0, item.href.length) === item.href;
                };
                scope.toggleSideNav = function() {
                    scope.displayMenu = !scope.displayMenu;
                };

                scope.followLink = function() {
                    scope.displayMenu = false;
                    elem.find('.open').removeClass('open');
                };

                scope.$on('$routeChangeSuccess', function() {
                    scope.displayMenu = false;
                    scope.currentRoute = $route.current;
                });
            }
        };
    }]);

    module.directive('sdMenu', function() {
        return {
            template: '<li ng-repeat="item in menu | orderBy:\'priority\'" sd-menu-item ng-class="{active: isActive(item)}"></li>'
        };
    });

    module.directive('sdMenuItem', function() {
        return {
            template: '<a ng-href="#{{ item.href }}" ng-click="followLink()" translate>{{ item.label }}</a>'
        };
    });
});
