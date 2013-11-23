define([
    'angular',
    'angular-route'
], function(angular) {
    'use strict';

    angular.module('superdesk.services.x', ['ngRoute'])
        .provider('x', ['menuProvider', '$routeProvider', function(menuProvider, $routeProvider) {
            return {
                $get: function() {
                    
                },
                x: function(id, item) {
                    if (typeof id === 'object' && item === undefined) {
                        item = id;
                        id = '';
                    } else if (item.menu !== false) {
                        menuProvider.menu(id, {
                            label: item.menuLabel || item.label,
                            href: item.menuHref || item.href,
                            priority: item.priority
                        });
                    }
                    var route = _.omit(_.extend({}, item), ['priority', 'href', 'menu', 'menuLabel', 'menuHref']);
                    $routeProvider.when(item.href, route);

                    return this;
                }
            };

        }]);

});