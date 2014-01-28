define(['angular'], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', 'workqueue',
    function($scope, superdesk, queue) {
        $scope.items = superdesk.data('ingest', {
            sort: ['firstcreated', 'desc'],
            filters: ['provider'],
            max_results: 25
        });

        $scope.queue = queue;

        $scope.openEditor = function() {
            superdesk.intent('edit', 'ingest', queue.active);
        };

        $scope.sidebar = false;
        $scope.sidebarstick = false;
        
    }];
});
