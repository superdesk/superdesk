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
                criteria.sort = formatSort(params.sort[0], params.sort[1]);
            } else {
                criteria.sort = formatSort('full_name', 'asc');
            }

            console.log(criteria);

            return criteria;
        }

        function fetchUsers(criteria) {
            api.users.query(criteria)
                .then(function(users) {
                    $scope.users = users;
                    $scope.createdUsers = [];
                });
        }

        function formatSort(key, dir) {
            var val = dir === 'asc' ? 1 : -1;
            switch (key) {
                case 'full_name':
                    return '[("first_name", ' + val + '), ("last_name", ' + val + ')]';
                default:
                    return '[("' + encodeURIComponent(key) + '", ' + val + ')]';
            }
        }

        $scope.$watch(getCriteria, fetchUsers, true);
    }

    return UserListController;
});
