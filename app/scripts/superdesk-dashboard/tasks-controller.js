define(['lodash'], function(_) {
    'use strict';

    TasksController.$inject = ['$scope', 'api', 'notify', 'userList', '$rootScope', 'es', 'desks'];
    function TasksController($scope, api, notify, userList, $rootScope, es, desks) {

        $scope.desksService = desks;
        $scope.selected = {};
        $scope.newTask = null;
        $scope.userLookup = {};

        userList.get(null, 1, 500)
        .then(function(result) {
            _.each(result._items, function(user) {
            	$scope.userLookup[user._id] = user;
            });
        });

        $scope.tasks = {};

        $scope.$watch(function() {
            return desks.getCurrentDeskId();
        }, function() {
            fetchTasks();
        });

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
            if ($scope.newTask.task.due_time) {
                $scope.newTask.task.due_date = new Date(
                    $scope.newTask.task.due_date.getFullYear(),
                    $scope.newTask.task.due_date.getMonth(),
                    $scope.newTask.task.due_date.getDate(),
                    $scope.newTask.task.due_time.getHours(),
                    $scope.newTask.task.due_time.getMinutes(),
                    $scope.newTask.task.due_time.getSeconds()
                );
            }
            delete $scope.newTask.task.due_time;

            api('tasks').save($scope.newTask)
            .then(function(result) {
                notify.success(gettext('Item saved.'));
                $scope.close();
                fetchTasks();
            });
        };

        $scope.close = function() {
            $scope.newTask = null;
        };

        var fetchTasks = function() {
            var filter = {term: {'task.user': $rootScope.currentUser._id}};
            if (desks.getCurrentDeskId()) {
                filter = {term: {'task.desk': desks.getCurrentDeskId()}};
            }
            api('tasks').query({
                source: {
                    size: 100,
                    sort: [{_updated: 'desc'}],
                    filter: filter
                }
            })
            .then(function(tasks) {
                $scope.tasks = tasks;
            });
        };

        fetchTasks();
    }

    return TasksController;
});
