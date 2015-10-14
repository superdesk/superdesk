/**
 * This file is part of Superdesk.
 *
 * Copyright 2015 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */
(function() {

'use strict';

WorkqueueService.$inject = ['session', 'api'];
function WorkqueueService(session, api) {

    this.items = [];

    /**
     * Get all items locked by current user
     */
    this.fetch = function() {
        return session.getIdentity()
            .then(angular.bind(this, function(identity) {
                return api.query('archive', {source: {filter: {term: {lock_user: identity._id}}}})
                    .then(angular.bind(this, function(res) {
                        this.items = null;
                        this.items = res._items || [];
                        return this.items;
                    }));
            }));
    };

    /**
     * Update given item
     */
    this.updateItem = function(itemId) {
        var old = _.find(this.items, {_id: itemId});
        if (old) {
            return api.find('archive', itemId).then(function(item) {
                return angular.extend(old, item);
            });
        }
    };
}

WorkqueueCtrl.$inject = ['$scope', '$route', 'workqueue', 'authoringWorkspace', 'multiEdit', 'superdesk', 'lock', '$location'];
function WorkqueueCtrl($scope, $route, workqueue, authoringWorkspace, multiEdit, superdesk, lock, $location) {

    $scope.active = null;
    $scope.workqueue = workqueue;
    $scope.multiEdit = multiEdit;

    $scope.$on('item:lock', updateWorkqueue);
    $scope.$on('item:unlock', updateWorkqueue);
    $scope.$on('$locationChangeSuccess', updateWorkqueue);
    $scope.$on('media_archive', function(e, data) {
        workqueue.updateItem(data.item);
    });

    updateWorkqueue();

    /**
     * Update list of opened items and set one active if its id is in current route path.
     */
    function updateWorkqueue() {
        workqueue.fetch().then(function() {
            var route = $route.current || {_id: null, params: {}};
            $scope.isMultiedit = route._id === 'multiedit';
            $scope.active = null;
            if (route.params.item) {
                $scope.active = _.find(workqueue.items, {_id: route.params.item});
            }
        });
    }

    $scope.openDashboard = function() {
        superdesk.intent('author', 'dashboard');
    };

    /**
     * Closes item. If item is opened, close authoring workspace.
     * Updates multiedit items, if item is part of multiedit.
     * When closing last item that was in multiedit(no more items in multiedit), redirects to monitoring.
     */
    $scope.closeItem = function(item) {
        lock.unlock(item);
        if (authoringWorkspace.item && item._id === authoringWorkspace.item._id){
            authoringWorkspace.close();
        }

        multiEdit.items = _.without(multiEdit.items, _.find(multiEdit.items, {article: item._id}));
        if (multiEdit.items.length === 0){
            $scope.redirectOnCloseMulti();
        }
    };

    $scope.openMulti = function() {
        $scope.isMultiedit = true;
        updateWorkqueue();
        multiEdit.open();
    };

    /**
     * Close multiedit.
     */
    $scope.closeMulti = function() {
        multiEdit.exit();
        $scope.redirectOnCloseMulti();
    };

    /**
     * If multi edit screen is opened, redirect to monitoring.
     */
    $scope.redirectOnCloseMulti = function() {
        if (this.isMultiedit){
            this.isMultiedit = false;
            $location.url('/workspace/monitoring');
        }
    };
}

WorkqueueListDirective.$inject = ['$rootScope', 'authoringWorkspace', '$location'];
function WorkqueueListDirective($rootScope, authoringWorkspace, $location) {
    return {
        templateUrl: 'scripts/superdesk-authoring/views/opened-articles.html',
        controller: 'Workqueue',
        scope: {},
        link: function(scope) {
            scope.edit = function(item, event) {
                if (!event.ctrlKey) {
                    scope.active = item;
                    authoringWorkspace.edit(item);
                    scope.redirectOnCloseMulti();

                    event.preventDefault();
                }
            };

            scope.link = function(item) {
                if (item) {
                    return $rootScope.link('authoring', item);
                }
            };
        }
    };
}

function ArticleDashboardDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/views/dashboard-articles.html',
        controller: 'Workqueue'
    };
}

angular.module('superdesk.authoring.workqueue', [
    'superdesk.activity',
    'superdesk.notification',
    'superdesk.authoring.multiedit'
])
    .service('workqueue', WorkqueueService)
    .controller('Workqueue', WorkqueueCtrl)
    .directive('sdWorkqueue', WorkqueueListDirective)
    .directive('sdDashboardArticles', ArticleDashboardDirective);
})();
