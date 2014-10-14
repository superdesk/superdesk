define([
    'angular',
    'lodash'
], function(angular, _) {
    'use strict';

    var constans = {
        MENU_MAIN: 'superdesk.menu.main',
        MENU_SETTINGS: 'superdesk.menu.settings',
        ACTION_EDIT: 'edit',
        ACTION_LIST: 'list',
        ACTION_VIEW: 'view',
        ACTION_PREVIEW: 'preview'
    };

    SuperdeskProvider.$inject = ['$routeProvider'];
    function SuperdeskProvider($routeProvider) {
        var widgets = {};
        var activities = {};
        var permissions = {};
        var panes = {};

        $routeProvider.when('/', {redirectTo: '/workspace'});

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
                reloadOnSearch: false,
                auth: true
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

        this.$get = ['$q', 'activityService', 'activityChooser', 'betaService',
        function($q, activityService, activityChooser, betaService) {

            /**
             * Render main menu depending on registered acitivites
             */
            var beta = betaService.isBeta();
            _.forEach(activities, function(activity, id) {
                if (activity.beta === true && beta === false) {
                    $routeProvider.when(activity.when, {redirectTo: '/workspace'});
                    delete activities[id];
                } else if (activity.when[0] === '/' && (activity.template || activity.templateUrl)) {
                    $routeProvider.when(activity.when, activity);
                }
            });

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
                 * Return activity by given id
                 */
                activity: function(id) {
                    return activities[id] || null;
                },

                /**
                 * Resolve an intent to a single activity
                 */
                resolve: function(intent) {
                    var activities = this.findActivities(intent);
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
                 * Find all available activities for given intent
                 */
                findActivities: function(intent) {
                    var criteria = {};
                    if (intent.action) {
                        criteria.action = intent.action;
                    }
                    if (intent.type) {
                        criteria.type = intent.type;
                    }
                    return _.filter(this.activities, function(activity) {
                        return _.find(activity.filters, criteria);
                    });
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
                }
            }, constans);
        }];
    }

    return SuperdeskProvider;
});
