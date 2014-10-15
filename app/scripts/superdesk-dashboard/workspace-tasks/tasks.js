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
                size: 100,
                sort: [{_updated: 'desc'}],
                filter: filter
            }
        })
        .then(function(tasks) {
            return tasks;
        });
    };
}

TasksController.$inject = ['$scope', 'api', 'notify', 'desks', 'tasks'];
function TasksController($scope, api, notify, desks, tasks) {

    $scope.selected = {};
    $scope.newTask = null;

    desks.initialize()
    .then(function() {
        $scope.deskLookup = desks.deskLookup;
        $scope.userLookup = desks.userLookup;
    });

    $scope.tasks = {};

    $scope.$watch(function() {
        return desks.getCurrentDeskId();
    }, function() {
        fetchTasks();
    });

    var fetchTasks = function() {
        tasks.fetch().then(function(list) {
            $scope.tasks = list;
        });
    };

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

    fetchTasks();
}

TaskPreviewDirective.$inject = ['tasks', 'notify'];
function TaskPreviewDirective(tasks, notify) {
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/task-preview.html',
        scope: {
            item: '=',
            users: '='
        },
        link: function(scope) {
            var _orig;
            scope.task = null;

            scope.$watch('item._id', function() {
                edit();
            });

            var edit = function() {
                scope.task = _.create(scope.item);
                _orig = scope.item;
            };

            scope.save = function(form) {
                tasks.save(_orig, scope.task)
                .then(function(result) {
                    notify.success(gettext('Item saved.'));
                    form.$setPristine();
                });
            };

            scope.cancel = function(form) {
                form.$setPristine();
                edit();
            };
        }
    };
}

AssigneeViewDirective.$inject = ['desks'];
function AssigneeViewDirective(desks) {
    desks.initialize();
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/assignee-view.html',
        scope: {item: '='},
        link: function(scope) {
            scope.deskLookup = desks.deskLookup;
            scope.userLookup = desks.userLookup;
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
