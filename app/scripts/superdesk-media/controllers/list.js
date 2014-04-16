define([], function() {
    'use strict';

    ArchiveListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function ArchiveListController($scope, $location, superdesk, api, es) {
        $scope.view = 'mgrid';
        $scope.$watch(getQuery, fetchItems, true);

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

        function getQuery() {
            var query = es($location.search());
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
