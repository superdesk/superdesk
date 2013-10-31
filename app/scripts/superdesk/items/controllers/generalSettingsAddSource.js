define(['angular'], function(angular){
    'use strict';

    return ['$scope','$modalInstance',
    function ($scope, $modalInstance) {
        $scope.closeModal = function () {
            $modalInstance.dismiss('cancel');
        };
    }];
});