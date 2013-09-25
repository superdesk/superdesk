define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.menu', []).
        directive('sdMenu', function($route) {
            return {
                templateUrl: 'scripts/superdesk/menu/menu.html',
                replace: true,
                priority: -1,
                link: function(scope, element, attrs) {
                    scope.title = attrs.title;
                    element.before('<li class="divider-vertical"></li>');
                    scope.items = [];
                    angular.forEach($route.routes, function(route) {
                        if ('menu' in route && route.menu.parent === attrs.sdMenu) {
                            scope.items.push(angular.extend({
                                path: route.originalPath,
                                priority: 0
                            }, route.menu));
                        }
                    });
                }
            };
        });
});
