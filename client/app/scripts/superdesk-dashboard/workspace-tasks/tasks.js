(function() {

'use strict';

TasksService.$inject = ['desks', '$rootScope', 'api', 'datetimeHelper'];
function TasksService(desks, $rootScope, api, datetimeHelper) {

    this.statuses =  [
        {_id: 'todo', name: gettext('To Do')},
        {_id: 'in_progress', name: gettext('In Progress')},
        {_id: 'done', name: gettext('Done')}
    ];

    this.save = function(orig, task) {
        if (task.task.due_time) {
            task.task.due_date = datetimeHelper.mergeDateTime(task.task.due_date, task.task.due_time).format();
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

    this.buildFilter = function(status) {
        var filters = [];
        var self = this;

        if (desks.getCurrentDeskId()) {
            //desk filter
            filters.push({term: {'task.desk': desks.getCurrentDeskId()}});
        } else {
            //user filter
            filters.push({term: {'task.user': $rootScope.currentUser._id}});
        }

        //status filter
        if (status) {
            filters.push({term: {'task.status': status}});
        } else {
            var allStatuses = [];
            _.each(self.statuses, function(s) {
                allStatuses.push({term: {'task.status': s._id}});
            });
            filters.push({or: allStatuses});
        }

        var and_filter = {and: filters};
        return and_filter;
    };

    this.fetch = function(status) {
        var filter = this.buildFilter(status);

        return api('tasks').query({
            source: {
                size: 25,
                sort: [{_updated: 'desc'}],
                filter: filter
            }
        });
    };
}

TasksController.$inject = ['$scope', '$timeout', 'api', 'notify', 'desks', 'tasks'];
function TasksController($scope, $timeout, api, notify, desks, tasks) {

    var KANBAN_VIEW = 'kanban',
        timeout;

    $scope.selected = {};
    $scope.newTask = null;
    $scope.tasks = null;
    $scope.view = KANBAN_VIEW;
    $scope.statuses = tasks.statuses;
    $scope.activeStatus = $scope.statuses[0]._id;

    $scope.$watch(function() {
        return desks.getCurrentDeskId();
    }, function() {
        fetchTasks();
    });

    function fetchTasks() {
        $timeout.cancel(timeout);
        timeout = $timeout(function() {
            var status = $scope.view === KANBAN_VIEW ? null : $scope.activeStatus;
            tasks.fetch(status).then(function(list) {
                $scope.tasks = list;
            });
        }, 300, false);
    }

    $scope.preview = function(item) {
        $scope.selected.preview = item;
    };

    $scope.create = function() {
        $scope.newTask = {
            task: {
                desk: desks.getCurrentDeskId(),
                due_date: moment().utc().format(),
                due_time: moment().utc().format('HH:mm:ss')
            }
        };
    };

    $scope.save = function() {
        tasks.save({}, $scope.newTask)
        .then(function(result) {
            notify.success(gettext('Item saved.'));
            $scope.close();
        });
    };

    $scope.close = function() {
        $scope.newTask = null;
    };

    $scope.setView = function(view) {
        if ($scope.view !== view) {
            $scope.view = view;
            $scope.tasks = null;
            fetchTasks();
        }
    };

    $scope.selectStatus = function(status) {
        if ($scope.activeStatus !== status) {
            $scope.activeStatus = status;
            $scope.tasks = null;
            fetchTasks();
        }
    };

    $scope.$on('task:new', fetchTasks);
    $scope.$on('task:stage', function(event, data) {
        var deskId = desks.getCurrentDeskId();
        if (deskId === data.old_desk || deskId === data.new_desk) {
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
                scope.task_details.due_time = moment(scope.item.task.due_date).utc().format('HH:mm:ss');
                _orig = scope.item;
            };
        }
    };
}

TaskKanbanBoardDirective.$inject = [];
function TaskKanbanBoardDirective() {
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/kanban-board.html',
        scope: {
            items: '=',
            status: '@',
            title: '@',
            selected: '='
        },
        link: function(scope) {
            scope.preview = function(item) {
                scope.selected.preview = item;
            };
        }
    };
}

AssigneeViewDirective.$inject = ['desks'];
function AssigneeViewDirective(desks) {
    var promise = desks.initialize();
    return {
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/assignee-view.html',
        scope: {
            task: '=',
            name: '=',
            avatarSize: '@'
        },
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

// todo(petr): move to desks module
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
                var stageId = stage ? stage._id : null;
                self.selected = stage || null;
                desks.setCurrentStageId(stageId);
            };

            // reload list of stages
            self.reload = function(deskId) {
                self.stages = deskId ? desks.deskStages[deskId] : null;
                self.select(_.find(self.stages, {_id: desks.activeStageId}));
            };

            $scope.$watch(function() {
                return desks.getCurrentDeskId();
            }, function() {
                self.reload(desks.getCurrentDeskId());
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
.directive('sdTaskKanbanBoard', TaskKanbanBoardDirective)

.service('tasks', TasksService)

.config(['superdeskProvider', function(superdesk) {

    superdesk.activity('/workspace/tasks', {
        label: gettext('Workspace'),
        controller: TasksController,
        templateUrl: 'scripts/superdesk-dashboard/workspace-tasks/views/workspace-tasks.html',
        topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
        sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
        filters: [{action: 'view', type: 'task'}]
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
