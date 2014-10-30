define([
    'angular',
    './baseList'
], function(angular, BaseListController) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$injector', 'superdesk', 'session', 'api', 'ViewsCtrl', 'ContentCtrl', 'StagesCtrl'];
    function ArchiveListController($scope, $injector, superdesk, session, api, ViewsCtrl, ContentCtrl, StagesCtrl) {

        var resource;
        var self = this;

        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.createdMedia = {
            items: []
        };

        $scope.currentModule = 'archive';
        $scope.views = new ViewsCtrl($scope);
        $scope.stages = new StagesCtrl($scope);
        $scope.content = new ContentCtrl($scope);
        $scope.type = 'archive';
        $scope.loading = false;

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
            $scope.loading = true;
            resource.query(criteria).then(function(items) {
                $scope.loading = false;
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            }, function() {
                $scope.loading = false;
            });
        };

        var refreshItems = _.debounce(_refresh, 1000);

        function _refresh() {
            if ($scope.selectedDesk) {
                resource = api('archive');
            } else {
                resource = api('user_content', session.identity);
            }
            self.refresh(true);
        }

        $scope.$on('media_archive', refreshItems);

        $scope.$watch(['stages.selected', 'selectedDesk'], refreshItems);

    }

    return ArchiveListController;
});
