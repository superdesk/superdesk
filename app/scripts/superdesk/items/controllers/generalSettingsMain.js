define(['angular'], function(angular){
    'use strict';

    return ['$scope','$modal', 'feedSources',
    function($scope, $modal, feedSources){
        $scope.save = function() {
        //do saving
        };

        $scope.addNewSource = function () {
            $modal.open({
                templateUrl: 'scripts/superdesk/items/views/generalSettingsAddSourceModal.html',
                controller: require('superdesk/items/controllers/generalSettingsAddSource'),
                windowClass: 'addSource'
            });
        };

        feedSources.get(function(data) {
            $scope.sources = data.sources;
        });
    }];
});