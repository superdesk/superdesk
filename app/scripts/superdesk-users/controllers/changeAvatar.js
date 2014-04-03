define([], function() {
    'use strict';

    ChangeAvatarController.$inject = ['$scope'];

    function ChangeAvatarController($scope) {
        
        $scope.preview = {
            url: ''
        };

        $scope.sources = [
            {
                title: 'Upload from computer',
                active: true
            },
            {
                title: 'Take a snapshot',
                active: false
            },
            {
                title: 'Use gravatar',
                active: false
            },
            {
                title: 'Specify a web URL',
                active: false
            },
            {
                title: 'Use default avatar',
                active: false
            }
            
        ];

        $scope.activate = function(index) {
            _.forEach($scope.sources, function(s) {
                s.active = false;
            });
            $scope.sources[index].active = true;
            $scope.preview.url = '';
        };
    }

    return ChangeAvatarController;
});
