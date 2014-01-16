define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'DataAdapter', function($scope, DataAdapter) {
        $scope.items = new DataAdapter('ingest', {
            where: {},
            sort: ['firstcreated', 'desc'],
            max_results: 25,
            filters: ['provider']
        });
    }];
});
