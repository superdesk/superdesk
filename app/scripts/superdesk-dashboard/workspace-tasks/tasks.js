(function() {

'use strict';

TasksService.$inject = ['desks', '$rootScope', 'api'];
function TasksService(desks, $rootScope, api) {

    this.save = function(orig, task) {
        if (task.task.due_time) {
            task.task.due_date = new Date(
                task.task.due_date.getFullYear(),
                task.task.due_date.getMonth(),
                task.task.due_date.getDate(),
                task.task.due_time.getHours(),
                task.task.due_time.getMinutes(),
                task.task.due_time.getSeconds()
            );
        }
        delete task.task.due_time;
        if (!task.task.user) {
            delete task.task.user;
        }

        return api('tasks').save(orig, task)
        .then(function(result) {
            return result;
        });
    };

    this.fetch = function() {
        var filter = {term: {'task.user': $rootScope.currentUser._id}};
        if (desks.getCurrentDeskId()) {
            filter = {term: {'task.desk': desks.getCurrentDeskId()}};
        }
        return api('tasks').query({
            source: {
                size: 25,
                sort: [{_updated: 'desc'}],
                filter: filter
            }
        });
    };
}

TasksController.$inject = ['$scope', 'api', 'notify', 'desks', 'tasks'];
function TasksController($scope, api, notify, desks, tasks) {

    $scope.selected = {};
    $scope.newTask = null;
    $scope.tasks = null;

    $scope.$watch(function() {
        return desks.getCurrentDeskId();
    }, fetchTasks);

    function fetchTasks() {
        tasks.fetch().then(function(list) {
            $scope.tasks = list;
        });
    }

    $scope.preview = function(item) {
        $scope.selected.preview = item;
    };

    $scope.create = function() {
        $scope.newTask = {
            task: {
                desk: desks.getCurrentDeskId(),
                due_date: new Date(new Date().getTime() + 24 * 60 * 60 * 1000),
                due_time: new Date(null, null, null, 12, 0, 0)
            }
        };
    };

    $scope.save = function() {
        tasks.save({}, $scope.newTask)
        .then(function(result) {
            notify.success(gettext('Item saved.'));
            $scope.close();
            fetchTasks();
        });
    };

    $scope.close = function() {
        $scope.newTask = null;
    };

    desks.initialize().then(function() {
        $scope.userLookup = desks.userLookup;
        $scope.deskLookup = desks.deskLookup;
    });
}

TaskPreviewDirective.$inject = ['tasks', 'desks', 'notify'];
function TaskPreviewDirective(tasks, desks, notify) {
    var promise = desks.initialize();
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/task-preview.html',
        scope: {
            item: '='
        },
        link: function(scope) {
            var _orig;
            scope.task = null;
            scope.task_details = null;
            scope.editmode = false;

            promise.then(function() {
                scope.desks = desks.deskLookup;
                scope.users = desks.userLookup;
            });

            scope.$watch('item._id', function(val) {
                if (val) {
                    scope.reset();
                }
            });

            scope.save = function() {
                scope.task.task = _.extend(scope.task.task, scope.task_details);
                tasks.save(_orig, scope.task)
                .then(function(result) {
                    notify.success(gettext('Item saved.'));
                    scope.editmode = false;
                });
            };

            scope.edit = function() {
                scope.editmode = true;
            };

            scope.reset = function() {
                scope.editmode = false;
                scope.task = _.create(scope.item);
                scope.task_details = _.extend({}, scope.item.task);
                scope.task_details.due_date = new Date(scope.item.task.due_date);
                scope.task_details.due_time = new Date(scope.item.task.due_date);
                _orig = scope.item;
            };
        }
    };
}

AssigneeViewDirective.$inject = ['desks'];
function AssigneeViewDirective(desks) {
    var promise = desks.initialize();
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/assignee-view.html',
        scope: {task: '='},
        link: function(scope) {
            promise.then(function setItemAssigne() {
                var task = angular.extend({desk: null, user: null}, scope.task);
                var desk = desks.deskLookup[task.desk] || {};
                var user = desks.userLookup[task.user] || {};
                scope.deskName = desk.name || null;
                scope.userName = user.display_name || null;
                scope.userPicture = user.picture_url || null;
            });
        }
    };
}

angular.module('superdesk.workspace.tasks', [])

.directive('sdTaskPreview', TaskPreviewDirective)
.directive('sdAssigneeView', AssigneeViewDirective)

.service('tasks', TasksService)

.config(['superdeskProvider', function(superdesk) {

    superdesk.activity('/workspace/tasks', {
        label: gettext('Workspace'),
        controller: TasksController,
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/workspace-tasks.html',
        topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
        beta: true
    });

    superdesk.activity('pick.task', {
        label: gettext('Pick task'),
        icon: 'pick',
        controller: ['data', 'superdesk',
            function pickTask(data, superdesk) {
                return superdesk.intent('author', 'article', data.item);
            }
        ],
        filters: [{action: superdesk.ACTION_EDIT, type: 'task'}]
    });
}]);

})();
