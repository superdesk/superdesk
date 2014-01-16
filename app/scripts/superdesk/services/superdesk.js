define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    var constans = {
        MENU_MAIN: 'superdesk.menu.main',
        MENU_SETTINGS: 'superdesk.menu.settings',

        ACTION_EDIT: 'edit',
        ACTION_LIST: 'list',
        ACTION_PREVIEW: 'preview'
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
         *
         * @param {string} id
         * @param {Object} data
         * @returns {Object} self
         */
        this.widget = function(id, data) {
            widgets[id] = angular.extend({_id: id, wcode: id}, data);
            return this;
        };

        /**
         * Register activity.
         *
         * @param {string} id
         * @param {Object} data
         * @returns {Object} self
         */
        this.activity = function(id, data) {
            var activity = angular.extend({
                _id: id,
                priority: 0,
                when: id, // use id as default
                href: id, // use id as default
                filters: []
            }, data);

            var actionless = _.find(activity.filters, function(filter) {
                return !filter.action;
            });

            if (actionless) {
                console.error('Missing filters action for activity', activity);
            }

            if (activity.when[0] === '/' && (activity.template || activity.templateUrl)) {
                $routeProvider.when(activity.when, activity);
            }

            activities[id] = activity;
            return this;
        };

        /**
         * Register permission.
         *
         * @param {string} id
         * @param {Object} data
         * @returns {Object} self
         */
        this.permission = function(id, data) {
            permissions[id] = angular.extend({_id: id}, data);
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
                    var activity = _.find(this.activities, function(activity) {
                        return _.find(activity.filters, {action: intent.action, type: intent.data});
                    });

                    if (activity) {
                        $location
                            .path(activity._id)
                            .search(_.pick(intent.extras, '_id'));
                        return intent;
                    }

                    console.log('No activity for intent found', intent);
                },

                /**
                 * Intent factory
                 */
                intent: function(action, data, extras) {
                    var intent = {
                        action: action,
                        data: data,
                        extras: extras
                    };

                    intentStack.push(intent);
                    return this.resolve(intent);
                },

                data: function(uri, options) {
                    return {};
                }
            }, constans);
        }];
    }]);

    module.run(['$rootScope', 'superdesk', function($rootScope, superdesk) {

        $rootScope.superdesk = superdesk; // add superdesk reference so we can use constants in templates

        $rootScope.intent = function() {
            superdesk.intent.apply(superdesk, arguments);
        };
    }]);

    /**
     * Directive for listing available activities for given category.
     */
    module.directive('sdActivityList', ['superdesk', function(superdesk) {
        return {
            scope: {
                data: '=',
                type: '@',
                action: '@'
            },
            template: '<li ng-repeat="activity in activities" sd-activity-item></li>',
            link: function(scope, elem, attrs) {
                var intent = {
                    action: scope.action
                };

                if (scope.type && scope.type !== '*') {
                    intent.type = scope.type;
                }

                if (!intent.action) {
                    console.error('No action set for intent in \'' + elem[0].outerHTML + '\'');
                }

                scope.activities = _.values(_.where(superdesk.activities, function(activity) {
                    return _.find(activity.filters, intent);
                }));
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
                        data: scope.data || {}
                    });

                    return !!ctrl;
                };
            }
        };
    }]);
});
