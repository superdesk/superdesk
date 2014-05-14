define(['lodash'], function(_) {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function ArchiveListController($scope, $location, superdesk, api, es) {
        $scope.view = 'mgrid';
        $scope.selected = {};
        $scope.createdMedia = {
            items: []
        };

        $scope.preview = function(item) {
            $scope.selected.preview = item;
        };

        $scope.display = function(item) {
            $scope.selected.view = item;
        };

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.createdMedia.items.unshift.apply($scope.createdMedia.items, items);
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
                var range = {versioncreated: {}};
                if (params.before) {
                    range.versioncreated.lte = params.before;
                }

                if (params.after) {
                    range.versioncreated.gte = params.after;
                }

                filters.push({range: range});
            }

            if (params.provider) {
                var provider = {
                    provider: params.provider
                };
                filters.push({term: provider});
            }

            return filters;
        }

        function getQuery(params) {
            var filters = buildFilters(params);
            var query = es(params, filters);
            query.sort = [{versioncreated: 'desc'}];
            return query;
        }

        function fetchItems(criteria) {
            api.archive.query(criteria).then(function(items) {
                $scope.items = items;
                $scope.createdMedia = {
                    items: []
                };
            });
        }
    }

    return ArchiveListController;
});
