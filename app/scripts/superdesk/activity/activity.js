define([
    'angular',
    'lodash',
    'require',
    './superdesk-service',
    './activity-list-directive',
    './activity-item-directive',
    './activity-chooser-directive',
    './activity-modal-directive'
], function(angular, _, require) {
    'use strict';

    var module = angular.module('superdesk.activity', [
        'ngRoute',
        'superdesk.translate',
        'superdesk.notify',
        'superdesk.services.modal',
        'superdesk.services.beta']);

    /**
     * Superdesk Provider for registering of app components.
     */
    module.provider('superdesk', require('./superdesk-service'));

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
            function execute (activity, locals) {
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
