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
         * Register an activity.
         *
         * @param {string} id Activity ID. Can be used for later lookup.
         * @param {Object} activityData Activity definition.
         *
         *    Object properties:
         *
         *    - `priority` - `{number}` - priority used for ordering.
         *    - `when` - `{string}` - $route.when param.
         *    - `href` - `{string}` - path for links generated for given activity.
         *    - `filters` - `{Array.<Object>}` - list of `action` `type` pairs.
         *    - `beta` - `{bool=false}` - is activity available only in beta mode?
         *    - `reloadOnSearch` - `{bool=false}` - $route.reloadOnSearch param.
         *    - `auth` - `{bool=true}` - does activity require authenticated user?
         *    - `features` - `{Object}` - map of features this activity requires.
         *
         * @returns {Object} self
         */
        this.activity = function(id, activityData) {
            var activity = angular.extend({
                _id: id,
                priority: 0,
                when: id, // use id as default
                href: id, // use id as default
                filters: [],
                beta: false,
                reloadOnSearch: false,
                auth: true,
                features: {}
            }, activityData);

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

        this.$get = ['$q', '$route', '$rootScope', 'activityService', 'activityChooser', 'betaService', 'features',
        function($q, $route, $rootScope, activityService, activityChooser, betaService, features) {

            /**
             * Render main menu depending on registered acitivites
             */
            betaService.isBeta().then(function(beta) {
                _.forEach(activities, function(activity, id) {
                    if (activity.beta === true && beta === false) {
                        $routeProvider.when(activity.when, {redirectTo: '/workspace'});
                        delete activities[id];
                    } else if (activity.when[0] === '/' && (activity.template || activity.templateUrl)) {
                        $routeProvider.when(activity.when, activity);
                    }
                });

                $route.reload();
            });

            /**
             * Let user to choose an activity
             */
            function chooseActivity(activities) {
                return activityChooser.choose(activities);
            }

            function checkFeatures(activity) {
                var isMatch = true;
                angular.forEach(activity.features, function(val, key) {
                    isMatch = isMatch && features[key] && val;
                });
                return isMatch;
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
                        return _.find(activity.filters, criteria) && checkFeatures(activity);
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
                    }, function() {
                        $rootScope.$broadcast([
                            'intent',
                            intent.action || '*',
                            intent.type || '*'
                        ].join(':'), intent);
                        return $q.reject();
                    });
                }
            }, constans);
        }];
    }

    return SuperdeskProvider;
});
