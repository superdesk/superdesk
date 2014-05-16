define(['lodash'], function(_) {
    'use strict';

    UserListController.$inject = ['$scope', '$location', 'api'];
    function UserListController($scope, $location, api) {
        $scope.maxResults = 25;

        $scope.selected = {user: null};
        $scope.createdUsers = [];

        $scope.preview = function(user) {
            $scope.selected.user = user;
        };

        $scope.createUser = function() {
            $scope.preview({});
        };

        $scope.closePreview = function() {
            $scope.preview(null);
        };

        $scope.afterDelete = function(data) {
            if ($scope.selected.user && data.item && data.item.href === $scope.selected.user.href) {
                $scope.selected.user = null;
            }
            fetchUsers(getCriteria());
        };

        // make sure saved user is presented in the list
        $scope.render = function(user) {
            if (_.find($scope.users._items, function(item) {
                return item._links.self.href === user._links.self.href;
            })) {
                return;
            }

            if (_.find($scope.createdUsers, function(item) {
                return item._links.self.href === user._links.self.href;
            })) {
                return;
            }

            $scope.createdUsers.unshift(user);
        };

        function getCriteria() {
            var params = $location.search(),
                criteria = {
                    max_results: $scope.maxResults
                };

            if (params.q) {
                criteria.where = JSON.stringify({
                    '$or': [
                        {username: {'$regex': params.q}},
                        {first_name: {'$regex': params.q}},
                        {last_name: {'$regex': params.q}},
                        {display_name: {'$regex': params.q}},
                        {email: {'$regex': params.q}}
                    ]
                });
            }

            if (params.page) {
                criteria.page = parseInt(params.page, 10);
            }

            if (params.sort) {
                criteria[params.sort[1]] = params.sort[0];
            }

            return criteria;
        }

        function fetchUsers(criteria) {
            api.users.query(criteria)
                .then(function(users) {
                    $scope.users = users;
                    $scope.createdUsers = [];
                });
        }

        $scope.$watch(getCriteria, fetchUsers, true);
    }

    return UserListController;
});
