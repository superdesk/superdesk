define([
    'angular',
    './baseList'
], function(angular, BaseListController) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$injector', 'superdesk', 'api', '$rootScope', 'ViewsCtrl'];
    function ArchiveListController($scope, $injector, superdesk, api, $rootScope, ViewsCtrl) {

        var resource;

        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.createdMedia = {
            items: []
        };

        $rootScope.currentModule = 'archive';
        $scope.views = new ViewsCtrl($scope);
        $scope.type = 'archive';

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.createdMedia.items.unshift.apply($scope.createdMedia.items, items);
            });
        };

        this.fetchItems = function(criteria) {
            if (resource == null) {
                return;
            }

            resource.query(criteria).then(function(items) {
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            });
        };

        $scope.$on('changes in media_archive', this.refresh);

        $scope.$watch('selectedDesk', angular.bind(this, function(desk) {
            resource = desk ? api('archive') : api('content', $rootScope.currentUser);
            this.refresh();
        }));
    }

    return ArchiveListController;
});
