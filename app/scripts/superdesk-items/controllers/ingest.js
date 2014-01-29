define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk',
    function($scope, superdesk) {
        $scope.items = superdesk.data('ingest', {
            sort: ['firstcreated', 'desc'],
            filters: ['provider'],
            max_results: 25
        });
    }];
});
