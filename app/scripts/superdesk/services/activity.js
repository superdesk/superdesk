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
     * Params:
     *
     * @param {string} id - activity id.
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
     * menu: (optional) Used to determine if activity will be displayed in navigation
     * menu or not. Default is true.
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
            var activities = {};

            return {
                $get: function() {
                    return activities;
                },
                activity: function(id, item) {
                    activities[id] = item;

                    if (item.menu !== false) {
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