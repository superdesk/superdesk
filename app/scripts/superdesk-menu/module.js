define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.menu', [])
        .directive('sdMenuWrapper', function($route){
            return {
                templateUrl: 'scripts/superdesk/views/sidebar-nav.html',
                replace: true,
                restrict: 'A',
                link: function(scope, element, attrs) {
                    scope.displayMenu = false;
                    scope.currentLink = '';
                    scope.toggleSideNav = function() {
                        scope.displayMenu = !scope.displayMenu;
                    };

                    scope.followLink = function() {
                        scope.displayMenu = false;
                        element.find('.open').removeClass('open');
                    };

                    scope.$on('$routeChangeSuccess', function() {
                        scope.currentLink = $route.current.menu || $route.current;
                    });
                }
            };
            
        })
        .directive('sdMenu', function($route) {
            var sdMenu = {
                templateUrl: 'scripts/superdesk-menu/menu.html',
                replace: false,
                priority: -1,
                link: function(scope, element, attrs) {
                    scope.items = [];
                    angular.forEach($route.routes, function(route) {
                        if ('menu' in route) {
                            var item = {label: route.menu.label, priority: route.menu.priority, href: route.originalPath};
                            if (route.menu.parent === undefined) {
                                scope.items.push(item);
                            } else {
                                var found = false;
                                for (var i = 0; i < scope.items.length; i++) {
                                    if (scope.items[i].label === route.menu.parent) {
                                        found = true;
                                        scope.items[i].items.push(item);
                                        break;
                                    }
                                }
                                if (found === false) {
                                    var maxPriority = sdMenu.getMaxPriority(scope.items);
                                    var parent = {label: route.menu.parent, priority: maxPriority + 1, items: [item]};
                                    scope.items.push(parent);
                                }
                            }
                        }
                    });
                },
                getMaxPriority: function(items) {
                    var maxPriority = 0;
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].priority > maxPriority) {
                            maxPriority = items[i].priority;
                        }
                    }
                    return maxPriority;
                }
            };
            
            return sdMenu;
        })
        .directive('sdToggleItem',function(){
            return {
                link: function(scope, element, attrs) {
                    element.on('click',function() {
                        element.parent().toggleClass('open');
                    });
                }
            };
        });
});
