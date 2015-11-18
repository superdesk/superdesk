define([
    'angular',
    'lodash',
    'require',
    './activity-list-directive',
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
         *    - `condition` - `{Function}` - method used to check if the activity is enabled for a specific item.
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
                privileges: {},
                condition: function(item) {return true;}
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

        this.$get = ['$q', '$route', '$rootScope', 'activityService', 'activityChooser',
            'betaService', 'features', 'privileges', '$injector',
            function superdeskFactory($q, $route, $rootScope, activityService, activityChooser, betaService,
                                      features, privileges, $injector) {

                /**
                 * Render main menu depending on registered acitivites
                 */
                betaService.isBeta().then(function(beta) {
                    _.forEach(activities, function(activity, id) {
                        if ((activity.beta === true && !beta) || !isAllowed(activity, beta)) {
                            $routeProvider.when(activity.when, {redirectTo: '/workspace'});
                        }
                    });
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
                    findActivities: function(intent, item) {
                        var criteria = {};
                        if (intent.action) {
                            criteria.action = intent.action;
                        }
                        if (intent.type) {
                            criteria.type = intent.type;
                        }

                        return _.sortBy(_.filter(this.activities, function(activity) {
                            return _.find(activity.filters, criteria) && isAllowed(activity) &&
                                activity.condition(item) && testAdditionalCondition();

                            function testAdditionalCondition() {
                                if (activity.additionalCondition) {
                                    return $injector.invoke(activity.additionalCondition, {}, {'item': item ? item : intent.data});
                                }

                                return true;
                            }
                        }), 'priority').reverse();
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

                        var self = this;

                        return this.resolve(intent).then(function(activity) {
                            return self.start(activity, intent);
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
                     * Get a link for given activity
                     *
                     * @param {string} activity
                     * @param {Object} data
                     * @returns {string}
                     */
                    link: function getSuperdeskLink(activity, data) {
                        return activityService.getLink(this.activity(activity), data);
                    },

                    /**
                     * Start activity
                     *
                     * @param {Object} activity
                     * @param {Object} locals
                     * @alias {activityService.start}
                     * @return {Promise}
                     */
                    start: function(activity, locals) {
                        return activityService.start(activity, locals);
                    },

                    /**
                     * Get activities based on menu category
                     *
                     * @param {string} category
                     */
                    getMenu: function getMenu(category) {
                        return privileges.loaded.then(function() {
                            var menu = [];
                            angular.forEach(activities, function(activity) {
                                if (activity.category === category && isAllowed(activity)) {
                                    menu.push(activity);
                                }
                            });

                            return menu;
                        });
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
        'superdesk.privileges',
        'superdesk.keyboard'
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
            if (activity.href[0] === '/') { // trigger route
                var matchAll = true,
                    path = activity.href.replace(/:([_a-zA-Z0-9]+)/, function(match, key) {
                        matchAll = matchAll && locals[key];
                        return locals[key] ? locals[key] : match;
                    });

                path = matchAll ? path : null;

                if (activity.href.indexOf('_type') !== -1 && !_.isNull(path)) {
                    path = path.replace(':_type', locals._type ? locals._type : 'archive');
                }

                return path;
            }
        }

        /**
         * Get URL for given activity
         *
         * @param {Object} activity
         * @param {Object} locals
         * @returns {string}
         */
        this.getLink = getPath;

        /**
         * Start given activity
         *
         * @param {object} activity
         * @param {object} locals
         * @returns {object} promise
         */
        this.start = function startActivity(activity, locals) {
            function execute(activity, locals) {
                var path = getPath(activity, locals && locals.data);
                if (path) { // trigger route
                    $location.path(path);
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

        $rootScope.link = function() {
            var path = superdesk.link.apply(superdesk, arguments);
            return path ? '#' + path : null;
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
     * Referrer service to set/get the referrer Url
     */
    module.service('referrer', function() {
        /**
         * Serving for the purpose of setting referrer url via referrer service, also setting url in localStorage. which is utilized to
         * get last working screen on authoring page if referrer url is unidentified
         * direct link(i.e from notification pane)
         *
         * @param {Object} currentRoute
         * @param {Object} previousRoute
         * @returns {string}
         */
        this.setReferrer = function(currentRoute, previousRoute) {
            if (currentRoute && previousRoute) {
                if ((currentRoute.$$route !== undefined) && (previousRoute.$$route !== undefined)) {
                    if (currentRoute.$$route.originalPath === '/') {
                        this.setReferrerUrl('/workspace');
                        localStorage.setItem('referrerUrl', '/workspace');
                        sessionStorage.removeItem('previewUrl');
                    } else {
                        if (currentRoute.$$route.authoring && (!previousRoute.$$route.authoring ||
                            previousRoute.$$route._id === 'packaging')) {
                            this.setReferrerUrl(prepareUrl(previousRoute));
                            localStorage.setItem('referrerUrl', this.getReferrerUrl());
                            sessionStorage.removeItem('previewUrl');
                        }
                    }
                }
            }
        };

        var referrerURL;
        this.setReferrerUrl = function(refURL) {
            referrerURL = refURL;
        };

        this.getReferrerUrl = function() {
            if (typeof (referrerURL) === 'undefined' || (referrerURL) === null) {
                if (typeof (localStorage.getItem('referrerUrl')) === 'undefined' || (localStorage.getItem('referrerUrl')) === null){
                    this.setReferrerUrl('/workspace');
                } else {
                    referrerURL = localStorage.getItem('referrerUrl');
                }
            }

            return referrerURL;
        };

        /**
         * Prepares complete Referrer Url from previous route href and querystring params(if exist),
         * e.g /workspace/content?q=test$repo=archive
         *
         * @param {Object} refRoute
         * @returns {string}
         */
        function prepareUrl(refRoute) {
            var completeUrl;
            if (refRoute) {
                completeUrl = refRoute.$$route.href.replace('/:_id', '');
                if (!_.isEqual({}, refRoute.pathParams)) {
                    completeUrl = completeUrl + '/' + refRoute.pathParams._id;
                }

                if (!_.isEqual({}, refRoute.params)) {
                    completeUrl = completeUrl + '?';
                    completeUrl = completeUrl + decodeURIComponent($.param(refRoute.params));
                }
            }
            return completeUrl;
        }
    });

    // reject modal on route change
    // todo(petr): what about blocking route change as long as it is opened?
    module.run(['$rootScope', 'activityService', 'referrer', function($rootScope, activityService, referrer) {
        $rootScope.$on('$routeChangeStart', function() {
            if (activityService.activityStack.length) {
                var item = activityService.activityStack.pop();
                item.defer.reject();
            }
        });

        $rootScope.$on('$routeChangeSuccess',  function(ev, currentRoute, previousRoute) {
            referrer.setReferrer(currentRoute, previousRoute);
        });
    }]);
    module.directive('sdActivityList', require('./activity-list-directive'));
    module.directive('sdActivityItem', ActivityItemDirective);
    module.directive('sdActivityChooser', require('./activity-chooser-directive'));
    module.directive('sdActivityModal', require('./activity-modal-directive'));

    ActivityItemDirective.$inject = ['asset'];
    function ActivityItemDirective(asset) {
        return {
            templateUrl: asset.templateUrl('superdesk/activity/views/activity-item.html')
        };
    }

    return module;
});
