define(['lodash'], function(_) {
    'use strict';

    UserListController.$inject = ['$scope', '$location', 'resource'];
    function UserListController($scope, $location, resource) {

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

        // make sure saved user is presented in the list
        $scope.render = function(user) {
            if (_.find($scope.users._items, {href: user.href})) {
                return;
            }

            if (_.find($scope.createdUsers, {href: user.href})) {
                return;
            }

            $scope.createdUsers.unshift(user);
        };

        function getCriteria() {
            var params = $location.search(),
                criteria = {
                    desc: 'createdOn',
                    maxResults: 25
                };

            if (params.q) {
                criteria.all = params.q + '%';
            }

            if (params.page) {
                criteria.offset = parseInt(params.page, 10) * criteria.maxResults;
            }

            return criteria;
        }

        $scope.$watch(getCriteria, function(criteria) {
            resource.users.query(criteria)
                .then(function(users) {
                    $scope.users = users;
                });
        }, true);
    }

    return UserListController;
});
