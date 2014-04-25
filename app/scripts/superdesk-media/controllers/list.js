define(['lodash'], function(_) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function ArchiveListController($scope, $location, superdesk, api, es) {
        $scope.view = 'mgrid';
        $scope.selected = {};

        $scope.preview = function(item) {
            $scope.selected.preview = item;
        };

        $scope.display = function(item) {
            $scope.selected.view = item;
        };

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.items.collection.unshift.apply($scope.items.collection, items);
            });
        };

        $scope.$watchCollection(function() {
            return $location.search();
        }, function(search) {
            var query = getQuery(search);
            fetchItems({source: query});
        });

        function buildFilters(params) {
            var filters = [];

            if (params.before || params.after) {
                var range = {VersionCreated: {}};
                if (params.before) {
                    range.VersionCreated.lte = params.before;
                }

                if (params.after) {
                    range.VersionCreated.gte = params.after;
                }

                filters.push({range: range});
            }

            return filters;
        }

        function getQuery(params) {
            var filters = buildFilters(params);
            return es(params, filters);
        }

        function fetchItems(criteria) {
            api.archive.query(criteria).then(function(items) {
                items._items = _.pluck(items.hits.hits, '_source');
                items.collection = items._items;
                $scope.items = items;
            });
        }
    }

    return ArchiveListController;
});
