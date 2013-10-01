define(['angular'], function(angular) {
    'use strict';

    return ['$scope', '$location', 'storage', 'users', 
    function($scope, $location, storage, users) {
        
        $scope.saveSettings = function() {
            storage.setItem('users:settings', $scope.settings, true);
        };

        $scope.loadSettings = function() {
            var settings = storage.getItem('users:settings');
            if (settings !== null) {
                $scope.settings = settings;
            } else {
                $scope.saveSettings();
            }
        };

        //
        $scope.users = users;
        console.log(users);

        $scope.settings = {
            fields: {
                avatar: true,
                display_name: true,
                username: false,
                email: false,
                _created: true
            }
        };

        $scope.loadSettings();
    }];
});
