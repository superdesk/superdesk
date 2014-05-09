define(['lodash'], function(_) {
    'use strict';

    UserListController.$inject = ['$scope', '$location', 'api'];
    function UserListController($scope, $location, api) {

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
                    maxResults: 25
                };

            if (params.q) {
                criteria.all = /%/.test(params.q) ? params.q : '%' + params.q + '%';
            }

            if (params.page) {
                criteria.offset = parseInt(params.page, 10) * criteria.maxResults;
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
