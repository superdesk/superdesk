(function() {

'use strict';

WorkqueueService.$inject = ['storage', 'preferencesService', 'notify'];
function WorkqueueService(storage, preferencesService, notify) {
    /**
     * Set items for further work, in next step of the workflow.
     */
    var queue = [];
    preferencesService.get('workqueue:items').then(function(result) {
        queue = result.items;
    });

    this.length = 0;
    this.active = null;

    /**
     * Add an item into queue
     *
     * it checks if item is in queue already and if yes it will move it to the very end
     *
     * @param {Object} item
     */
    this.add = function(item) {
        _.remove(queue, {_id: item._id});
        queue.unshift(item);
        this.length = queue.length;
        this.active = item;
        this.save();
        return this;
    };

    /**
     * Update item in a queue
     */
    this.update = function(item) {
        if (item) {
            var base = this.find({_id: item._id});
            queue[_.indexOf(queue, base)] = _.extend(base, item);
            this.save();
        }
    };

    /**
     * Get first item
     */
    this.first = function() {
        return _.first(queue);
    };

    /**
     * Get all items from queue
     */
    this.all = function() {
        return queue;
    };

    /**
     * Save queue to local storage
     */
    this.save = function() {

        var update = {
            'workqueue:items': {
                'items': queue
            }
        };

        preferencesService.update(update, 'workqueue:items').then(function() {
                //nothing to do
            }, function(response) {
                notify.error(gettext('User preference could not be saved...'));
        });
    };

    /**
     * Find item by given criteria
     */
    this.find = function(criteria) {
        return _.find(queue, criteria);
    };

    /**
     * Set given item as active
     */
    this.setActive = function(item) {
        if (!item) {
            this.active = null;
        } else {
            this.active = this.find({_id: item._id});
        }
    };

    /**
     * Get '_id' of active item or null if it's not defined
     */
    this.getActive = function() {
        return this.active ? this.active._id : null;
    };

    /**
     * Remove given item from queue
     */
    this.remove = function(item) {
        _.remove(queue, {_id: item._id});
        this.length = queue.length;
        this.save();

        if (this.active._id === item._id && this.length > 0) {
            this.setActive(_.first(queue));
        } else {
            this.active = null;
        }
    };
}

WorkqueueCtrl.$inject = ['$scope', 'workqueue', 'superdesk', 'ContentCtrl'];
function WorkqueueCtrl($scope, workqueue, superdesk, ContentCtrl) {
    $scope.workqueue = workqueue.all();
    $scope.content = new ContentCtrl();

    $scope.openItem = function(article) {
        if ($scope.active) {
            $scope.update();
        }
        workqueue.setActive(article);
        superdesk.intent('author', 'article', article);
    };

    $scope.openDashboard = function() {
        superdesk.intent('author', 'dashboard');
    };

    $scope.closeItem = function(item) {
        if ($scope.active) {
            $scope.close();
        } else {
            workqueue.remove(item);
            superdesk.intent('author', 'dashboard');
        }
    };
}

function WorkqueueListDirective() {
    return {
        templateUrl: 'scripts/superdesk-authoring/views/opened-articles.html',
        scope: {
            active: '=',
            update: '&',
            close: '&'
        },
        controller: WorkqueueCtrl
    };
}

angular.module('superdesk.authoring.workqueue', ['superdesk.activity'])
    .service('workqueue', WorkqueueService)
    .directive('sdWorkqueue', WorkqueueListDirective)

    .config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/authoring/', {
                label: gettext('Authoring'),
                templateUrl: 'scripts/superdesk-authoring/views/dashboard.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                beta: true,
                controller: WorkqueueCtrl,
                category: superdesk.MENU_MAIN,
                filters: [{action: 'author', type: 'dashboard'}]
            });
    }]);
})();
