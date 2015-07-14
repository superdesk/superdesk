define([
    'angular',
    './baseList'
], function(angular, BaseListController) {
    'use strict';

    ArchiveListController.$inject = [
        '$scope', '$injector', '$location', '$q', '$timeout', 'superdesk',
        'session', 'api', 'desks', 'ContentCtrl', 'StagesCtrl', 'notify', 'multi'
    ];
    function ArchiveListController($scope, $injector, $location, $q, $timeout, superdesk, session, api, desks, ContentCtrl,
        StagesCtrl, notify, multi) {

        var resource,
            self = this;

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
        $scope.published = !!$location.search().published;

        $scope.togglePublished = function togglePublished() {
            if ($scope.spike) {
                $scope.toggleSpike();
            }

            $scope.published = !$scope.published;
            $location.search('published', $scope.published ? '1' : null);
            $location.search('_id', null);
            $scope.stages.select(null);
        };

        $scope.toggleSpike = function toggleSpike() {
            if ($scope.published) {
                $scope.togglePublished();
            }

            $scope.spike = !$scope.spike;
            $location.search('spike', $scope.spike ? 1 : null);
            $location.search('_id', null);
            $scope.stages.select(null);
        };

        $scope.stageSelect = function(stage) {
            if ($scope.spike) {
                $scope.toggleSpike();
            }

            if ($scope.published) {
                $scope.togglePublished();
            }

            $scope.stages.select(stage);
            multi.reset();
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

        this.fetchItem = function fetchItem(id) {
            if (resource == null) {
                return $q.reject(id);
            }

            return resource.getById(id);
        };

        var refreshPromise,
            refreshItems = function() {
                $timeout.cancel(refreshPromise);
                refreshPromise = $timeout(_refresh, 100, false);
            };

        function _refresh() {
            if (desks.active.desk) {
                if ($scope.published) {
                    resource = api('published');
                } else {
                    resource = api('archive');
                }
            } else {
                resource = api('user_content', session.identity);
            }
            self.refresh(true);
        }

        function reset(event, data) {
            if (data && data.item) {
                if ($location.search()._id === data.item) {
                    $location.search('_id', null);
                }
            }
            refreshItems();
        }

        $scope.$on('task:stage', function(_e, data) {
            if ($scope.stages.selected && (
                $scope.stages.selected._id === data.new_stage ||
                $scope.stages.selected._id === data.old_stage)) {
                refreshItems();
            }
        });

        $scope.$on('media_archive', refreshItems);
        $scope.$on('item:fetch', refreshItems);
        $scope.$on('item:copy', refreshItems);
        $scope.$on('item:take', refreshItems);
        $scope.$on('item:duplicate', refreshItems);
        $scope.$on('item:created', refreshItems);
        $scope.$on('item:updated', refreshItems);
        $scope.$on('item:replaced', refreshItems);
        $scope.$on('item:deleted', refreshItems);
        $scope.$on('item:mark', refreshItems);
        $scope.$on('item:spike', refreshItems);
        $scope.$on('item:unspike', reset);

        $scope.$on('item:publish:closed:channels', function(_e, data) {
            if (desks.activeDeskId && desks.activeDeskId === data.desk) {
                notify.error(gettext('Item having story name ' + data.unique_name + ' published to closed Output Channel(s).'));
                refreshItems();
            }
        });

        desks.fetchCurrentUserDesks().then(function() {
            // only watch desk/stage after we get current user desk
            $scope.$watch(function() {
                return desks.active;
            }, function(active) {
                $scope.selected = active;
                if ($location.search().page) {
                    $location.search('page', null);
                    return; // will reload via $routeUpdate
                }

                refreshItems();
            });
        });

        // reload on route change if there is still the same _id
        var oldQuery = _.omit($location.search(), '_id', 'fetch');
        $scope.$on('$routeUpdate', function(e, route) {
            var query = _.omit($location.search(), '_id', 'fetch');
            if (!angular.equals(oldQuery, query)) {
                refreshItems();
            }
            oldQuery = query;
        });
    }

    return ArchiveListController;
});
