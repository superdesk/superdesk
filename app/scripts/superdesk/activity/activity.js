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
                features: {},
                privileges: {}
            }, activityData);

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

        this.$get = ['$q', '$route', '$rootScope', 'activityService', 'activityChooser', 'betaService', 'features', 'privileges',
        function superdeskFactory($q, $route, $rootScope, activityService, activityChooser, betaService, features, privileges) {

            /**
             * Render main menu depending on registered acitivites
             */
            betaService.isBeta().then(function(beta) {
                _.forEach(activities, function(activity, id) {
                    if ((activity.beta === true && !beta) || !isAllowed(activity, beta)) {
                        $routeProvider.when(activity.when, {redirectTo: '/workspace'});
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

            function checkPrivileges(activity) {
                return privileges.userHasPrivileges(activity.privileges);
            }

            /**
             * Test if user is allowed to use given activity.
             *   Testing is based on current server setup (features) and user privileges.
             *
             * @param {Object} activity
             */
            function isAllowed(activity) {
                return checkFeatures(activity) && checkPrivileges(activity);
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
                        return _.find(activity.filters, criteria) && isAllowed(activity);
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
                },

                /**
                 * Get activities based on menu category
                 *
                 * @param {string} category
                 */
                getMenu: function getMenu(category) {
                    var menu = [];
                    angular.forEach(activities, function(activity) {
                        if (activity.category === category && isAllowed(activity)) {
                            menu.push(activity);
                        }
                    });

                    return $q.when(menu);
                }
            }, constans);
        }];
    }

    var module = angular.module('superdesk.activity', [
        'ngRoute',
        'superdesk.notify',
        'superdesk.features',
        'superdesk.translate',
        'superdesk.services.beta',
        'superdesk.services.modal',
        'superdesk.privileges'
    ]);

    module.provider('superdesk', SuperdeskProvider);

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
            return activity.when.replace(/:([_a-zA-Z0-9]+)/, function(match, key) {
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
            function execute(activity, locals) {
                if (activity.when[0] === '/') { // trigger route
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
                return modal.confirm(gettext(activity.confirm)).then(function runConfirmed() {
                    return execute(activity, locals);
                }, function() {
                    return $q.reject({confirm: 1});
                });
            } else {
                return execute(activity, locals);
            }
        };

    }]);

    module.run(['$rootScope', 'superdesk', function($rootScope, superdesk) {

        $rootScope.superdesk = superdesk; // add superdesk reference so we can use constants in templates

        $rootScope.intent = function() {
            return superdesk.intent.apply(superdesk, arguments);
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
