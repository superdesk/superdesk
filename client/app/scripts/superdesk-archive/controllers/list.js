define([
    'angular',
    './baseList'
], function(angular, BaseListController) {
    'use strict';

    ArchiveListController.$inject = [
        '$scope', '$injector', '$location', '$timeout', '$q',
        'superdesk', 'session', 'api', 'desks', 'ContentCtrl', 'StagesCtrl', '$anchorScroll'
    ];
    function ArchiveListController($scope, $injector, $location, $timeout, $q, superdesk, session, api, desks, ContentCtrl, StagesCtrl,
        $anchorScroll) {

        var resource,
            timeout,
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

        $scope.toggleSpike = function toggleSpike() {
            $scope.spike = !$scope.spike;
            $location.search('spike', $scope.spike ? 1 : null);
            $location.search('_id', null);
            $scope.stages.select(null);
        };
        $scope.fetching = false;
        $scope.page = 1;
        $scope.cacheNextItems = [];
        $scope.cachePreviousItems = [];

        $scope.stageSelect = function(stage) {
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
            resource.query(criteria)
            .then(function(items) {
                $scope.loading = false;
                $scope.items = items;

                $scope.cachePreviousItems = items._items;
                setNextItems(criteria);
            }, function() {
                $scope.loading = false;
            });
        };
        $scope.fetchNext = function() {
            if (!$scope.fetching) {

                if ($scope.cacheNextItems.length > 0) {
                    $scope.fetching = true;
                    var resource = self.getResource();
                    $scope.page = $scope.page + 1;
                    var query = self.getQuery(_.omit($location.search(), '_id'), true);
                    query.from = ($scope.page) * query.size;

                    var criteria = {source: query};
                    $scope.loading = true;

                    if ($scope.items._items.length > query.size){
                        $scope.cachePreviousItems = _.slice($scope.items._items, 0, query.size);
                        $scope.items._items.splice(0, query.size);
                    }
                    $timeout(function() {
                        $scope.items._items = $scope.items._items.concat($scope.cacheNextItems);
                    }, 100);

                    resource.query(criteria)
                    .then(function(items) {
                        $scope.cacheNextItems = items._items;
                        $scope.fetching = false;
                        return true;
                    }, function() {
                        //
                    })
                    ['finally'](function() {
                        $scope.loading = false;
                    });
                }
            } else {
                return $q.when(false);
            }
        };

        function scrollList(id) {
            $location.hash(id);
            $anchorScroll();
        }

        $scope.fetchPrevious = function() {
            if (!$scope.fetching && $scope.page > 2) {
                $scope.fetching = true;
                var resource = self.getResource();
                $scope.page = $scope.page - 1;
                var query = self.getQuery(_.omit($location.search(), '_id'), true);
                if ($scope.page > 2) {
                    query.from = ($scope.page - 3) * query.size;
                } else {
                    query.from = 0;
                }
                var criteria = {source: query};
                $scope.loading = true;

                if ($scope.items._items.length > query.size) {
                    $scope.cacheNextItems = _.slice($scope.items._items,
                        $scope.items._items.length - ($scope.items._items.length - query.size), $scope.items._items.length);
                    $scope.items._items.splice($scope.items._items.length - ($scope.items._items.length - query.size), query.size);
                }

                $timeout(function() {
                    $scope.items._items.unshift.apply($scope.items._items, $scope.cachePreviousItems);
                    if ($scope.items._items.length > 0) {
                        scrollList($scope.items._items[parseInt((($scope.items._items.length - 1) / 2), 10)]._id);
                    }
                }, 100);

                resource.query(criteria)
                .then(function(items) {
                    $scope.cachePreviousItems = items._items;
                    $scope.fetching = false;
                }, function() {
                    //
                })
                ['finally'](function() {
                    $scope.loading = false;
                });
            }
        };

        function setNextItems(criteria) {
            criteria.source.from = $scope.page * criteria.source.size;
            return resource.query(criteria)
                .then(function(items) {
                    $scope.cacheNextItems = items._items;
                }, function() {
                    //
                });
        }

        this.getResource  = function getResource() {
            return desks.activeDeskId ? api('archive') : api('user_content', session.identity);
        };
        function refreshItems() {
            $timeout.cancel(timeout);
            timeout = $timeout(_refresh, 100, false);
        }

        function _refresh() {
            resource = self.getResource();
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
        $scope.$on('item:duplicate', refreshItems);
        $scope.$on('item:created', refreshItems);
        $scope.$on('item:updated', refreshItems);
        $scope.$on('item:replaced', refreshItems);
        $scope.$on('item:deleted', refreshItems);
        $scope.$on('item:mark', refreshItems);
        $scope.$on('item:spike', refreshItems);
        $scope.$on('item:unspike', reset);

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
