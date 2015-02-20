define([
    'angular',
    './baseList'
], function(angular, BaseListController) {
    'use strict';

    ArchiveListController.$inject = [
        '$scope', '$injector', '$location',
        'superdesk', 'session', 'api', 'desks', 'ContentCtrl', 'StagesCtrl'
    ];
    function ArchiveListController($scope, $injector, $location, superdesk, session, api, desks, ContentCtrl, StagesCtrl) {

        var resource;
        var self = this;

        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.currentModule = 'archive';
        $scope.stages = new StagesCtrl($scope);
        $scope.content = new ContentCtrl($scope);
        $scope.type = 'archive';
        $scope.repo = {
            ingest: false,
            archive: true
        };
        $scope.loading = false;
        $scope.spike = !!$location.search().spike;

        desks.fetchCurrentUserDesks()
        .then(function(userDesks) {
            $scope.selected.desk = _.find(userDesks._items, {_id: desks.getCurrentDeskId()});
        });

        $scope.toggleSpike = function toggleSpike() {
            $scope.spike = !$scope.spike;
            $scope.stages.select(null);
            $location.search('spike', $scope.spike ? 1 : null);
            $location.search('_id', null);
        };

        $scope.stageSelect = function(stage) {
            initpage();
            if ($scope.spike) {
                $scope.toggleSpike();
            }
            $scope.stages.select(stage);
        };

        $scope.openUpload = function openUpload() {
            superdesk.intent('upload', 'media');
        };

        this.fetchItems = function fetchItems(criteria) {
            if (resource == null) {
                return;
            }
            $scope.loading = true;
            resource.query(criteria).then(function(items) {
                $scope.loading = false;
                $scope.items = items;
            }, function() {
                $scope.loading = false;
            });
        };

        var refreshItems = _.debounce(_refresh, 100);

        function _refresh() {
            if ($scope.selected.desk) {
                resource = api('archive');
            } else {
                resource = api('user_content', session.identity);
            }
            self.refresh(true);
        }

        $scope.$on('task:stage', function(_e, data) {
        	if ($scope.stages.selected &&
        	    ($scope.stages.selected._id === data.new_stage ||
        	     $scope.stages.selected._id === data.old_stage)) {
        		refreshItems();
        	}
        });

        $scope.$on('media_archive', refreshItems);
        $scope.$on('item:fetch', refreshItems);
        $scope.$on('item:spike', refreshItems);
        $scope.$on('item:unspike', refreshItems);
        $scope.$watchGroup(['stages.selected', 'selected.desk'], refreshItems);

        $scope.$watch('selected.desk', initpage);
        function initpage() {
            $location.search('page', null);
        }

        // reload on route change if there is still the same _id
        var oldQuery = _.omit($location.search(), '_id');
        $scope.$on('$routeUpdate', function(e, route) {
            var query = _.omit($location.search(), '_id');
            if (!angular.equals(oldQuery, query)) {
                refreshItems();
            }
            oldQuery = query;
        });
    }

    return ArchiveListController;
});
