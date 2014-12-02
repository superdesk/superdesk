(function(){
	'use strict';

	var app = angular.module('superdesk.stream', [
        'superdesk.activity',
        'superdesk.asset'
    ]);
    app.controller('StreamController', ['$scope', 'api', '$rootScope', function($scope, api, $rootScope) {
        $scope.selectedDesk = null;
        $scope.selectionName = 'My Activity';
        $scope.selectedDeskId = null;

        console.log('root', $rootScope);

        api('desks').query().then(function(result) {
            console.log('got desks', $scope.desks);
            $scope.desks = result._items;
        });
        console.log('desks', $scope.desks);

        $scope.select = function(desk) {
            console.log('selection name', $scope.selectionName, $scope.selectedDeskId);
            $scope.selectedDesk = desk;
            $scope.selectedDeskId = null;
            if ($scope.selectedDesk !== null) {
                $scope.selectionName = desk.name;
                $scope.selectedDeskId = $scope.selectedDesk._id;
            } else {
                $scope.selectionName = 'My Activity';
            }
            console.log('selection name', $scope.selectionName, $scope.selectedDeskId);

            api('activity').query({embedded:{'user':1}, where:{'desk':$scope.selectedDeskId}})
            .then(function(result) {
                $scope.activities = [];
                result._items.forEach(function(activity, index, array) {
                    activity.display_message = activity.message;
                    for (var tag in activity.data) {
                        var tagRegex = new RegExp('{{\\s*'+tag+'\\s*}}', 'gi');
                        activity.display_message = activity.display_message.replace(tagRegex, activity.data[tag]);
                    }
                    $scope.activities.push(activity);
                });
                console.log('activities', $scope.activities);
            });
        };

        var reload = function() {
            $scope.select($scope.selectedDesk);
        };

        $rootScope.$on('activity', function(_e, extras) {
            reload();
        });

        reload();
    }])
    .config(['superdeskProvider', 'assetProvider', 'gettext', function(superdesk, asset, gettext) {
        superdesk.activity('/workspace/stream', {
            label: gettext('Workspace'),
            controller: 'StreamController',
            templateUrl: asset.templateUrl('superdesk-stream/views/workspace-stream.html'),
            topTemplateUrl: asset.templateUrl('superdesk-dashboard/views/workspace-topnav.html'),
            beta: true
        });
    }]);
})();
