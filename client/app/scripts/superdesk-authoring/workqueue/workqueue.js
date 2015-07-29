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

ArticleDashboardCtrl.$inject = ['$scope', 'ContentCtrl'];
function ArticleDashboardCtrl($scope, ContentCtrl) {
    $scope.content = new ContentCtrl();
}

WorkqueueCtrl.$inject = ['$scope', '$route', 'workqueue', 'multiEdit', 'superdesk', 'lock'];
function WorkqueueCtrl($scope, $route, workqueue, multiEdit, superdesk, lock) {

    $scope.active = null;
    $scope.workqueue = workqueue;
    $scope.multiEdit = multiEdit;

    updateWorkqueue();

    $scope.$on('$routeChangeSuccess', updateWorkqueue);
    $scope.$on('item:lock', updateWorkqueue);
    $scope.$on('item:unlock', updateWorkqueue);
    $scope.$on('media_archive', function(e, data) {
        workqueue.updateItem(data.item);
    });

    /**
     * Update list of opened items and set one active if its id is in current route path.
     */
    function updateWorkqueue() {
        workqueue.fetch().then(function() {
            var route = $route.current || {_id: null, params: {}};
            $scope.isMultiedit = route._id === 'multiedit';
            $scope.active = null;
            if (route.params._id) {
                $scope.active = _.find(workqueue.items, {_id: route.params._id});
            }
        });
    }

    $scope.openDashboard = function() {
        superdesk.intent('author', 'dashboard');
    };

    $scope.closeItem = function(item) {
        lock.unlock(item).then(updateWorkqueue);
    };

    $scope.openMulti = function() {
        multiEdit.open();
    };

    $scope.closeMulti = function() {
        multiEdit.exit();
    };
}

function WorkqueueListDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/views/opened-articles.html',
        controller: 'Workqueue'
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
    .directive('sdDashboardArticles', ArticleDashboardDirective)

    .config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/authoring/', {
                label: gettext('Authoring'),
                description: gettext('Create articles'),
                templateUrl: 'scripts/superdesk-authoring/views/dashboard.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                beta: true,
                controller: ArticleDashboardCtrl,
                category: superdesk.MENU_MAIN,
                filters: [{action: 'author', type: 'dashboard'}]
            });
    }]);
})();
