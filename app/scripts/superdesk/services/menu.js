define(['angular'], function(angular) {
    'use strict';

    /**
     * Menu service
     *
     * Menu service provides methods for plugins to register menu items
     * which are used to construct main navigation menu.
     * 
     * Usage:
     * 
     * Registering a menu item:
     *
     * menuProvider.register({
     *     id: 'dashboard'
     *     label: gettext('Dashboard'),
     *     href: '/',
     *     priority: 0,
     *     parentId: null
     * });
     */
    angular.module('superdesk.services.menu', [])
        .provider('menu', [function() {
            var menu = {};

            var getContainer = function(id) {
                if (!id) {
                    return menu;
                } else {
                    return findContainer(id, menu);
                }
            };

            var findContainer = function(id, container) {
                var found = false;
                _.forEach(container, function(item, itemId) {
                    if (itemId === id) {
                        if (!item.children) {
                            item.children = {};
                        }
                        found = item.children;
                    } else {
                        found = findContainer(id, item.children);
                    }
                });
                return found;
            };

            return {
                $get: function() {
                    return menu;
                },
                register: function(item) {
                    var parent = getContainer(item.parentId);
                    parent[item.id] = {
                        label: item.label,
                        href: item.href,
                        priority: item.priority
                    }
                }
            };

        }]);

});