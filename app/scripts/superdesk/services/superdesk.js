define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    var constans = {
        MENU_MAIN: 'superdesk.menu.main',
        MENU_SETTINGS: 'superdesk.menu.settings'
    };

    var module = angular.module('superdesk.services');

    /**
     * Superdesk Provider for registering of app components.
     */
    module.provider('superdesk', ['$routeProvider', function($routeProvider) {
        var widgets = {};
        var activities = {};
        var permissions = {};

        angular.extend(this, constans);

        /**
         * Register widget.
         */
        this.widget = function(key, data) {
            widgets[key] = angular.extend({_id: key, wcode: key}, data);
            return this;
        };

        /**
         * Register activity.
         */
        this.activity = function(key, data) {
            activities[key] = angular.extend({
                _id: key,
                priority: 0,
                href: data.when || null // use when as menu.item.href if href not set
            }, data);

            var when = data.when || data.href;
            if (when != null) {
                $routeProvider.when(when, activities[key]);
            }

            return this;
        };

        /**
         * Register permission.
         */
        this.permission = function(key, data) {
            permissions[key] = angular.extend({_id: key}, data);
            return this;
        };

        this.$get = ['$q', '$location', function($q, $location) {
            var intentStack = [];
            return angular.extend({
                widgets: widgets,
                activities: activities,
                permissions: permissions,

                /**
                 * Resolve an intent
                 */
                resolve: function(intent) {
                    console.log('resolve', intent);
                    intentStack.push(intent);
                }
            }, constans);
        }];
    }]);

    module.run(['$rootScope', 'intent', function($rootScope, intent) {
        $rootScope.intent = intent;
    }]);

    module.factory('intent', ['superdesk', function(superdesk) {
        function Intent(action, data, extras) {
            this.action = action;
            this.data = data;
            this.extras = extras;
        }

        return function (action, data, extras) {
            var intent = new Intent(action, data, extras);
            superdesk.resolve(intent);
        };
    }]);

    /**
     * Directive for listing available activities for given category.
     */
    module.directive('sdActivityList', ['superdesk', function(superdesk) {
        return {
            scope: {item: '='},
            template: '<li ng-repeat="activity in activities" sd-activity-item data-activity="activity"></li>',
            link: function(scope, elem, attrs) {
                scope.activities = _.values(_.where(superdesk.activities, {category: attrs.sdActivityList}));
            }
        };
    }]);

    /**
     * Directive for single activity which runs activity on click.
     */
    module.directive('sdActivityItem', ['$window', '$controller', 'gettext', function($window, $controller, gettext) {
        return {
            template: '<a href="" ng-click="run(activity)" translate>{{ activity.label }}</a>',
            link: function(scope, elem, attrs) {
                scope.run = function(activity) {
                    if (activity.confirm && !$window.confirm(gettext(activity.confirm))) {
                        return;
                    }

                    var ctrl = $controller(activity.controller, {
                        data: scope.item || {}
                    });

                    return !!ctrl;
                };
            }
        };
    }]);
});
