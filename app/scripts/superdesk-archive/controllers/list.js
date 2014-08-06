define([
    'lodash',
    './baseList'
], function(_, BaseListController) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$injector', 'superdesk', 'api', '$rootScope', 'ViewsCtrl'];
    function ArchiveListController($scope, $injector, superdesk, api, $rootScope, ViewsCtrl) {

        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.createdMedia = {
            items: []
        };

        $scope.views = new ViewsCtrl($scope);
        $scope.type = 'archive';
        $scope.api = api.ingest;

        $rootScope.currentModule = 'archive';

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.createdMedia.items.unshift.apply($scope.createdMedia.items, items);
            });
        };

        this.fetchItems = function(criteria) {
    		api.archive.query(criteria).then(function(items) {
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            });
        };
        $scope.$on('changes in media_archive', this.refresh);
    }

    return ArchiveListController;
});
