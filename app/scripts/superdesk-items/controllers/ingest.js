define(['angular', 'moment'], function(angular, moment) {
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

        $scope.search = {
            type : {
                text : true,
                audio : false,
                video : false,
                picture : true,
                graphic : false,
                composite : false
            },
            general : {
                urgencyfrom : 1,
                urgencyto : 3,
                versioncreated : {
                    startDate : null,
                    endDate : null
                },
                provider : null,
                creditline : null,
                place : null
            }
        };
        
    }];
});
