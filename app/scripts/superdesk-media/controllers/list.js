define([
    'angular'
], function(angular) {
    'use strict';

    return ['$scope', 'superdesk', 'api', function($scope, superdesk, api) {
        var getCriteria = function() {
            return {
                desc: 'createdOn'
            };
        };

        var fetchItems = function(criteria) {
            api.image.query().then(function(items) {
                $scope.items = items;
            });
        };

        $scope.$watch(getCriteria, fetchItems, true);

        $scope.view = 'mgrid';

        $scope.preview = function(item) {
            $scope.previewItem = item;
        };

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media');
        };
    }];
});
