define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    var constans = {
        MENU_MAIN: 'superdesk.menu.main',
        MENU_SETTINGS: 'superdesk.menu.settings',

        ACTION_EDIT: 'edit',
        ACTION_LIST: 'list',
        ACTION_VIEW: 'view',
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
        var panes = {};

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
         * Register widget.
         */
        this.pane = function(key, data) {
            panes[key] = angular.extend({_id: key}, data);
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
                filters: [],
                reloadOnSearch: false
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

        this.$get = ['$q', '$location', '$controller', '$window', 'activityChooser', 'DataAdapter',
        function($q, $location, $controller, $window, activityChooser, DataAdapter) {

            /**
             * Find all available activities for given intent
             */
            function findActivities(intent) {
                return _.filter(activities, function(activity) {
                    return _.find(activity.filters, {action: intent.action, type: intent.data});
                });
            }

            /**
             * Start given activity
             */
            function startActivity(activity, intent) {
                var defer = $q.defer();

                if (activity.confirm && !$window.confirm(gettext(activity.confirm))) {
                    defer.reject();
                } else {
                    defer.resolve($controller(activity.controller, intent));
                }

                return defer.promise;
            }

            /**
             * Let user to choose an activity
             */
            function chooseActivity(activities) {
                return activityChooser.choose(activities);
            }

            return angular.extend({
                widgets: widgets,
                activities: activities,
                permissions: permissions,
                panes: panes,

                /**
                 * Resolve an intent to a single activity
                 */
                resolve: function(intent) {
                    var defer = $q.defer(),
                        activities = findActivities(intent);
                    switch (activities.length) {
                        case 0:
                            defer.reject();
                            break;

                        case 1:
                            defer.resolve(activities[0]);
                            break;

                        default:
                            chooseActivity(activities).then(function(activity) {
                                defer.resolve(activity);
                            }, function() {
                                defer.reject();
                            });
                    }

                    return defer.promise;
                },

                /**
                 * Intent factory
                 *
                 * starts an activity for given action and data
                 *
                 * @param {string} action
                 * @param {string} data type
                 * @param {Object} extras
                 * @returns {Object} promise
                 */
                intent: function(action, data, extras) {
                    var intent = {
                        action: action,
                        data: data,
                        extras: extras
                    };

                    var defer = $q.defer();
                    this.resolve(intent).then(function(activity) {
                        if (activity._id[0] === '/') { // trigger route
                            $location
                                .path(activity._id)
                                .search(_.pick(intent.extras, '_id'));
                            defer.resolve(intent);
                            return;
                        }

                        startActivity(activity, intent).then(function(res) {
                            defer.resolve(res);
                        }, function(reason) {
                            console.info('activity failed', reason);
                            defer.reject();
                        });
                    }, function(reason) {
                        console.info('activity not resolved', reason);
                        defer.reject();
                    });

                    return defer.promise;
                },

                data: function(resource, params) {
                    return new DataAdapter(resource, params);
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

                if (!scope.type) { // guess item type by self href
                    intent.type = scope.data._links.self.href.split('/')[1];
                } else {
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
            replace : true,
            template: '<li class="item-field" ng-click="run(activity)" title="{{activity.label}}"><i class="icon-{{ activity.icon }}" ng-show="activity.icon"></i><span translate>{{ activity.label }}</span></li>',
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

    /**
     * Activity chooser service - bridge between superdesk and activity chooser directive
     */
    module.service('activityChooser', ['$q', function($q) {
        var defer;

        this.choose = function(activities) {
            defer = $q.defer();
            this.activities = activities;
            return defer.promise;
        };

        this.resolve = function(activity) {
            this.activities = null;
            defer.resolve(activity);
        };

        this.reject = function() {
            this.activities = null;
            defer.reject();
        };
    }]);

    /**
     * Render a popup with activities so user can choose one
     */
    module.directive('sdActivityChooser', ['activityChooser', function(activityChooser) {
        return {
            scope: {},
            templateUrl: 'scripts/superdesk/views/activityChooser.html',
            link: function(scope, elem, attrs) {
                scope.chooser = activityChooser;
            }
        };
    }]);
});
