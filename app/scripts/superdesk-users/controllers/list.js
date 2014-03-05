define([], function() {
    'use strict';

    UserListController.$inject = ['$scope', '$http', '$q', 'locationParams', 'superdesk'];
    function UserListController($scope, $http, $q, locationParams, superdesk) {

        $scope.selectedUser = null;

        $http.get('http://superdesk.apiary.io/HR/User/')
            .success(function(data) {
                $scope.users = data;
                $scope.users._items = data.collection;
            });

        $scope.preview = function(user) {
            $scope.selectedUser = user;
        };

        $scope.closePreview = function() {
            $scope.selectedUser = null;
        };
    }

    return UserListController;
});
