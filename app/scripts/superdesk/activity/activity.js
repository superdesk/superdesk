define([
    'angular',
    'lodash',
    'require',
    './activity-list-directive',
    './activity-item-directive',
    './activity-chooser-directive',
    './activity-modal-directive'
], function(angular, _, require) {
    'use strict';

    var constans = {
        MENU_MAIN: 'superdesk.menu.main',
        MENU_SETTINGS: 'superdesk.menu.settings',
        ACTION_EDIT: 'edit',
        ACTION_LIST: 'list',
        ACTION_VIEW: 'view',
        ACTION_PREVIEW: 'preview'
    };

    var module = angular.module('superdesk.activity', []);

    /**
     * Superdesk Provider for registering of app components.
     */
    module.provider('superdesk', ['$routeProvider', function($routeProvider) {
        var widgets = {};
        var activities = {};
        var permissions = {};
        var panes = {};

        $routeProvider.when('/', {redirectTo: '/dashboard'});

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
                beta: false,
                reloadOnSearch: false
            }, data);

            var actionless = _.find(activity.filters, function(filter) {
                return !filter.action;
            });

            if (actionless) {
                console.error('Missing filters action for activity', activity);
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

        this.$get = ['$q', 'activityService', 'activityChooser', 'DataAdapter', 'betaService',
        function($q, activityService, activityChooser, DataAdapter, betaService) {

            /**
             * Render main menu depending on registered acitivites
             */
            var beta = betaService.isBeta();
            _.forEach(activities, function(activity, id) {
                if (activity.beta === true && beta === false) {
                    $routeProvider.when(activity.when, {redirectTo: '/dashboard'});
                    delete activities[id];
                } else if (activity.when[0] === '/' && (activity.template || activity.templateUrl)) {
                    $routeProvider.when(activity.when, activity);
                }
            });

            /**
             * Find all available activities for given intent
             */
            function findActivities(intent) {
                return _.filter(activities, function(activity) {
                    return _.find(activity.filters, {action: intent.action, type: intent.type});
                });
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
                    var activities = findActivities(intent);
                    switch (activities.length) {
                        case 0:
                            return $q.reject();

                        case 1:
                            return $q.when(activities[0]);

                        default:
                            return chooseActivity(activities);
                    }
                },

                /**
                 * Intent factory
                 *
                 * starts an activity for given action and data
                 *
                 * @param {string} action
                 * @param {string} type
                 * @param {Object} data
                 * @returns {Object} promise
                 */
                intent: function(action, type, data) {

                    var intent = {
                        action: action,
                        type: type,
                        data: data
                    };

                    return this.resolve(intent).then(function(activity) {
                        return activityService.start(activity, intent);
                    });
                },

                data: function(resource, params) {
                    return new DataAdapter(resource, params);
                }
            }, constans);
        }];
    }]);

    module.service('activityService', ['$location', '$injector', '$q', '$timeout', 'gettext', 'modal',
    function($location, $injector, $q, $timeout, gettext, modal) {

        var activityStack = [];
        this.activityStack = activityStack;

        /**
         * Expand path using given locals, eg. with /users/:Id and locals {Id: 2} returns /users/2
         *
         * @param {Object} activity
         * @param {Object} locals
         * @returns {string}
         */
        function getPath(activity, locals) {
            return activity.when.replace(/:([a-zA-Z0-9]+)/, function(match, key) {
                return locals[key] ? locals[key] : match;
            });
        }

        /**
         * Start given activity
         *
         * @param {object} activity
         * @param {object} locals
         * @returns {object} promise
         */
        this.start = function startActivity(activity, locals) {
            function execute (activity, locals) {
                if (activity._id[0] === '/') { // trigger route
                    $location.path(getPath(activity, locals.data));
                    return $q.when(locals);
                }

                if (activity.modal) {
                    var defer = $q.defer();
                    activityStack.push({
                        defer: defer,
                        activity: activity,
                        locals: locals
                    });
                    return defer.promise;
                } else {
                    return $q.when($injector.invoke(activity.controller, {}, locals));
                }
            }

            if (activity.confirm) {
                return modal.confirm(gettext(activity.confirm)).then(function() {
                    return execute(activity, locals);
                }, function() {
                    return $q.reject('no confirm');
                });
            } else {
                return execute(activity, locals);
            }
        };

    }]);

    module.run(['$rootScope', 'superdesk', function($rootScope, superdesk) {

        $rootScope.superdesk = superdesk; // add superdesk reference so we can use constants in templates

        $rootScope.intent = function() {
            superdesk.intent.apply(superdesk, arguments);
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

    // reject modal on route change
    // todo(petr): what about blocking route change as long as it is opened?
    module.run(['$rootScope', 'activityService', function($rootScope, activityService) {
        $rootScope.$on('$routeChangeStart', function() {
            if (activityService.activityStack.length) {
                var item = activityService.activityStack.pop();
                item.defer.reject();
            }
        });
    }]);

    module.directive('sdActivityList', require('./activity-list-directive'));
    module.directive('sdActivityItem', require('./activity-item-directive'));
    module.directive('sdActivityChooser', require('./activity-chooser-directive'));
    module.directive('sdActivityModal', require('./activity-modal-directive'));

    return module;
});
