define([], function() {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function ArchiveListController($scope, $location, superdesk, api, es) {
        $scope.view = 'mgrid';

        $scope.$watch(function() {
            return $location.search();
        }, function(search) {
            fetchItems(getQuery(search));
        });

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

        function buildFilters(params) {
            if (params.before || params.after) {
                var range = {ChangeOn: {}};
                if (params.before) {
                    range.ChangeOn.lte = params.before;
                }

                if (params.after) {
                    range.ChangeOn.gte = params.after;
                }

                params.filters = [{range: range}];
            }
        }

        function getQuery(params) {
            buildFilters(params);
            var query = es(params);
            console.log(query);
            return { // todo(petr) replace with elastic
                desc: 'q.createdOn'
            };
        }

        function fetchItems(criteria) {
            api.image.query(criteria).then(function(items) {
                $scope.items = items;
            });
        }
    }

    return ArchiveListController;
});
