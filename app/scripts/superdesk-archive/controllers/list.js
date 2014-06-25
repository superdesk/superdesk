define([
    'lodash',
    './baseList'
], function(_, BaseListController) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$injector', 'superdesk', 'api'];
    function ArchiveListController($scope, $injector, superdesk, api) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.createdMedia = {
            items: []
        };

        $scope.type = 'archive';

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.createdMedia.items.unshift.apply($scope.createdMedia.items, items);
            });
        };

        var self = this;
        this.fetchItems = function(criteria) {
        	self.fetchItemsCriteria = criteria;
    		api.archive.query(criteria).then(function(items) {
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            });
        };
        $scope.$on('changes in media_archive', function() {
        	self.fetchItems(self.fetchItemsCriteria);
        });
    }

    return ArchiveListController;
});
