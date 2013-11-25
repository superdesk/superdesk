define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.menu', [])
        .directive('sdMenuWrapper', ['$route', 'menu', function($route, menu){
            return {
                templateUrl: 'scripts/superdesk/views/sidebar-nav.html',
                replace: true,
                restrict: 'A',
                link: function(scope, element, attrs) {
                    scope.menu = menu;
                    scope.displayMenu = false;
                    scope.activeLabel = '';
                    scope.toggleSideNav = function() {
                        scope.displayMenu = !scope.displayMenu;
                    };

                    scope.followLink = function() {
                        scope.displayMenu = false;
                        element.find('.open').removeClass('open');
                    };

                    scope.$on('$routeChangeSuccess', function() {
                        scope.displayMenu = false;
                        scope.activeLabel = $route.current.label;
                    });
                }
            };
        }])
        .directive('sdMenu', ['$route', function($route) {
            return {
                templateUrl: 'scripts/superdesk-menu/menu.html',
                replace: false,
                scope: {items: '=', activeLabel: '='},
                priority: -1,
                link: function(scope, element, attrs) {
                    scope.itemsArray = _.values(scope.items);
                }
            };
        }])
        .directive('sdMenuItem', ['$compile', function($compile) {
            return {
                templateUrl: 'scripts/superdesk-menu/menuItem.html',
                replace: false,
                scope: {item: '='},
                priority: -1,
                link: function(scope, element, attrs) {
                    var subMenu = $compile('<ul sd-menu data-items="item.children">')(scope);
                    element.append(subMenu);
                }
            };
        }])
        .directive('sdToggleItem', [function(){
            return {
                link: function(scope, element, attrs) {
                    element.on('click',function() {
                        element.parent().toggleClass('open');
                    });
                }
            };
        }]);
});
