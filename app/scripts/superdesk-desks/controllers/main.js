define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk',
    function($scope, superdesk) {
        $scope.desks = superdesk.data('desks');
        $scope.desks.query();
    }];
});
