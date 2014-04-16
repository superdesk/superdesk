define([], function() {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api'];
    function ArchiveListController($scope, $location, superdesk, api) {
        $scope.view = 'mgrid';
        $scope.$watch(getQuery, fetchItems, true);

        $scope.preview = function(item) {
            $scope.previewItem = item;
        };

        $scope.openUpload = function() {
            superdesk.intent('upload', 'media').then(function(items) {
                // todo: put somewhere else
                $scope.items.collection.unshift.apply($scope.items.collection, items);
            });
        };

        function getQuery() {
            var search = $location.search(),
                query = {
                    size: 50,
                    from: search.from || 0
                };

            if (search.q) {
                query.filtered = {
                    query: {
                        term: {HeadLine: search.q}
                    }
                };
            }

            return {
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
