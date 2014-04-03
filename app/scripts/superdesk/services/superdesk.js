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
     * Directive for listing available activities for given category.
     */
    module.directive('sdActivityList', ['superdesk', function(superdesk) {
        return {
            scope: {
                data: '=',
                type: '@',
                action: '@',
                done: '='
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
    module.directive('sdActivityItem', ['activityService', function(activityService) {
        return {
            replace: true,
            template: [
                '<li class="item-field" ng-click="run(activity, $event)" title="{{activity.label}}">',
                '<i class="icon-{{ activity.icon }}" ng-show="activity.icon"></i>',
                '<span translate>{{ activity.label }}</span>',
                '</li>'
            ].join(''),
            link: function(scope, elem, attrs) {
                scope.run = function(activity, e) {
                    e.stopPropagation();
                    activityService.start(activity, {data: scope.data}).then(function() {
                        if (typeof scope.done === 'function') {
                            scope.done(scope.data);
                        }
                    });
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
    module.directive('sdActivityChooser', ['activityChooser', 'keyboardManager', function(activityChooser, keyboardManager) {
        return {
            scope: {},
            templateUrl: 'scripts/superdesk/views/activityChooser.html',
            link: function(scope, elem, attrs) {
                var UP = - 1,
                    DOWN = 1;

                scope.chooser = activityChooser;
                scope.selected = null;

                function move(diff, items) {
                    var index = _.indexOf(items, scope.selected),
                        next = _.max([0, _.min([items.length - 1, index + diff])]);
                    scope.selected = items[next];
                }

                scope.$watch(function() {
                    return activityChooser.activities;
                }, function(activities, prev) {
                    scope.selected = activities ? _.first(activities) : null;

                    if (activities) {
                        keyboardManager.push('up', function() {
                            move(UP, activities);
                        });

                        keyboardManager.push('down', function() {
                            move(DOWN, activities);
                        });

                        keyboardManager.push('enter', function() {
                            activityChooser.resolve(scope.selected);
                        });
                    } else if (prev) {
                        keyboardManager.pop('up');
                        keyboardManager.pop('down');
                        keyboardManager.pop('enter');
                    }
                });

                scope.select = function(activity) {
                    scope.selected = activity;
                };
            }
        };
    }]);

    module.directive('sdActivityModal', function(activityService) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk/views/activity-modal.html',
            link: function(scope, elem) {
                scope.stack = activityService.activityStack;
                scope.$watch('stack.length', function(len) {
                    scope.activity = null;
                    if (len) {
                        var config = scope.stack[len - 1];
                        scope.activity = config.activity;
                        scope.locals = config.locals;

                        scope.reject = function(reason) {
                            return config.defer.reject(reason);
                        };

                        scope.resolve = function(result) {
                            return config.defer.resolve(result);
                        };

                        config.defer.promise['finally'](function() {
                            scope.stack.pop();
                        });
                    }
                });
            }
        };
    });
});
