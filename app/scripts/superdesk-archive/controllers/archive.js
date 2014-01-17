define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', function($scope, superdesk) {
        $scope.items = superdesk.data('ingest', {
            where: {},
            sort: ['firstcreated', 'desc'],
            max_results: 25,
            filters: ['provider']
        });
    }];
});
