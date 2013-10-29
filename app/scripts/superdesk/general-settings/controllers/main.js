define(['angular'], function(angular){
    'use strict';

    return ['$scope','$modal', 'feedSources',
      function($scope, $modal, feedSources){

            feedSources.get(function(data) {
                $scope.sources = data.sources;
            });

            $scope.save = function() {
            //do saving
            };

            $scope.addNewSource = function () {
		        $modal.open({
                    templateUrl : 'scripts/superdesk/general-settings/views/addSourceModal.html',
                    controller : 'AddSourceModalCtrl',
                    windowClass : 'addSource'
		        });
		    };
        }];
});