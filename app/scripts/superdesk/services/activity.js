define([
    'angular',
    'angular-route'
], function(angular) {
    'use strict';

    /**
     * Activity service
     *
     * Activity service is used to configure both menuProvider and $routeProvider,
     * as they have many common elements.
     * 
     * Usage:
     * 
     * Registering an activity:
     *
     * activityProvider.activity(id, options);
     *
     * or (if no menu item is needed)
     *
     * activityProvider.activity(options);
     *
     * Params:
     *
     * @param {string} id - activity id. Currently only passed to menuProvider
     * for managing relationships between menu items. If not provided, activity
     * is not listed in the menu.
     *
     * @param {object} options - options for activity. Additionally, any option that
     * needs to be passed to $routeProvider (controller, templateUrl) can be added
     * to options.
     *
     * Available options are:
     * href: (mandatory) Directly passed to menuProvider and $routeProvider for
     * defining url.
     *
     * label: (mandatory) Used for display name used in $routeProvider and
     * (if menuLabel is not provided) menuProvider.
     *
     * priority: (optional) Used for sorting menu items.
     *
     * menuLabel: (optional) If menu label needs to be different than route, this
     * is used to override label for menuProvider.
     *
     * menuHref: (optional) If menu href needs to be different than route, this
     * is used to override route for menuProvider.
     *
     * parent: (optional) Directly passed to menu provider, to manage menu hierarchy.
     *
     */
    angular.module('superdesk.services.activity', ['ngRoute'])
        .provider('activity', ['menuProvider', '$routeProvider', function(menuProvider, $routeProvider) {
            return {
                $get: function() {
                    
                },
                activity: function(id, item) {
                    if (typeof id === 'object' && item === undefined) {
                        item = id;
                        id = '';
                    } else {
                        menuProvider.menu(id, {
                            label: item.menuLabel || item.label,
                            href: item.menuHref || item.href,
                            priority: item.priority,
                            parent: item.parent
                        });
                    }
                    var route = _.omit(_.extend({}, item), ['priority', 'href', 'menuLabel', 'menuHref']);
                    $routeProvider.when(item.href, route);

                    return this;
                }
            };

        }]);

});