define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', function($scope, superdesk) {
        $scope.items = superdesk.data('archive', {
            max_results: 25,
            sort: ['firstcreated', 'desc'],
            filters: ['provider']
        });
    }];
});
