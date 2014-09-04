define(['lodash'], function(_) {
    'use strict';

    TasksController.$inject = ['$scope', 'api', 'notify'];
    function TasksController($scope, api, notify) {

        $scope.selected = {};
        $scope.newTask = null;
        $scope.userLookup = null;

        $scope.tasks = {};

        $scope.preview = function(item) {
            $scope.selected.preview = item;
        };

        $scope.create = function() {
            $scope.newTask = {};
        };

        $scope.save = function() {
            if ($scope.newTask.due_time && $scope.newTask.due_time) {
                $scope.newTask.due_date.setTime($scope.newTask.due_time.getTime());
            }
            delete $scope.newTask.due_time;

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
            api('tasks').query()
            .then(function(tasks) {
                $scope.tasks = tasks;
            });
        };

        var fetchUsers = function() {
            api.users.query()
            .then(function(result) {
                $scope.userLookup = {};
                _.each(result._items, function(user) {
                    $scope.userLookup[user._id] = user;
                });
            });
        };

        fetchTasks();
        fetchUsers();

    }

    return TasksController;
});
