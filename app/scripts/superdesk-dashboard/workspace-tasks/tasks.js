(function() {

'use strict';

TasksService.$inject = ['desks', '$rootScope', 'api'];
function TasksService(desks, $rootScope, api) {

    this.save = function(orig, task) {
        if (task.task.due_time) {
            task.task.due_date =
                moment(task.task.due_date)
                .set('hour', task.task.due_time.getHours())
                .set('minute', task.task.due_time.getMinutes())
                .set('second', task.task.due_time.getSeconds())
                .utc();
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

    this.buildFilter = function() {
        var filter;
        if (desks.getCurrentStageId()) {
            filter = {term: {'task.stage': desks.getCurrentStageId()}};
        } else if (desks.getCurrentDeskId()) {
            filter = {term: {'task.desk': desks.getCurrentDeskId()}};
        } else {
            filter = {term: {'task.user': $rootScope.currentUser._id}};
        }
        return filter;
    };

    this.fetch = function() {
        var filter = this.buildFilter();

        return api('tasks').query({
            source: {
                size: 25,
                sort: [{_updated: 'desc'}],
                filter: filter
            }
        });
    };
}

TasksController.$inject = ['$scope', 'api', 'notify', 'desks', 'tasks', 'StagesCtrl'];
function TasksController($scope, api, notify, desks, tasks, StagesCtrl) {

    $scope.selected = {};
    $scope.newTask = null;
    $scope.tasks = null;
    $scope.stages = new StagesCtrl($scope);

    $scope.$watch(function() {
        return desks.getCurrentDeskId();
    }, function() {
        fetchTasks();
    });

    var fetchTasks = _.debounce(fetch, 300);

    function fetch() {
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
                due_date: moment().utc().format(),
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

    $scope.$watch('stages.selected', function(stage, stageOld) {
        if (stage || stageOld) {
            fetchTasks();
        }
    });
}

TaskPreviewDirective.$inject = ['tasks', 'desks', 'notify'];
function TaskPreviewDirective(tasks, desks, notify) {
    var promise = desks.initialize();
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/task-preview.html',
        scope: {
            item: '=',
            close: '&onclose'
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
                scope.task_details.due_date = moment(scope.item.task.due_date).utc().format();
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

StagesCtrlFactory.$inject = ['api', 'desks'];
function StagesCtrlFactory(api, desks) {

    var promise = desks.initialize();
    return function StagesCtrl($scope) {
        var self = this;
        promise.then(function() {

            self.stages = null;
            self.selected = null;

            // select a stage as active
            self.select = function(stage) {
                self.selected = stage || null;
                var stageId = stage ? stage._id : null;
                desks.setCurrentStageId(stageId);
            };

            // reload list of stages
            self.reload = function(deskId) {
                if (deskId) {
                    self.stages = desks.deskStages[deskId];
                } else {
                    self.stages = null;
                }
                self.select(_.find(self.stages, {_id: desks.getCurrentStageId()}));
            };

            $scope.$watch(function() {
                return desks.getCurrentDeskId();
            }, function(_deskId) {
                self.reload(_deskId || null);
            });

        });
    };
}

function DeskStagesDirective() {
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/desk-stages.html'
    };
}

 angular.module('superdesk.workspace.tasks', [])

.factory('StagesCtrl', StagesCtrlFactory)

.directive('sdTaskPreview', TaskPreviewDirective)
.directive('sdAssigneeView', AssigneeViewDirective)
.directive('sdDeskStages', DeskStagesDirective)

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
