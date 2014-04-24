define([], function() {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function ArchiveListController($scope, $location, superdesk, api, es) {
        $scope.view = 'mgrid';

        $scope.preview = function(item) {
            $scope.previewItem = item;
        };

        $scope.display = function(item) {
            $scope.viewItem = item;
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
            console.log(query);
            //fetchItems(query);
        });

        function buildFilters(params) {
            var filters = [];

            if (params.before || params.after) {
                var range = {ChangeOn: {}};
                if (params.before) {
                    range.ChangeOn.lte = params.before;
                }

                if (params.after) {
                    range.ChangeOn.gte = params.after;
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
                console.log(items);
            });
        }
    }

    return ArchiveListController;
});
