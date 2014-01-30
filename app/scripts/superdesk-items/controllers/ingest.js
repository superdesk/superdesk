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
        $scope.sidebarstick = true;


        $scope.search = {
            content : {
                audio : false,
                video : false,
                text : true,
                images : true,
                packages : false
            },
            general : {
                urgencyfrom : 1,
                urgencyto : 3,
                versionupdated : '02/02/2013',
                provider : '',
                creditline : '',
                place : ''
            }
        };
        
    }];
});
