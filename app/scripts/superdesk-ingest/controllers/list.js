define([
    'lodash',
    'superdesk-archive/controllers/baseList'
], function(_, BaseListController) {
    'use strict';

    IngestListController.$inject = ['$scope', '$injector', '$location', 'api', '$rootScope'];
    function IngestListController($scope, $injector, $location, api, $rootScope) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.type = 'ingest';
        $scope.repo = {
            ingest: true,
            archive: false
        };
        $scope.api = api.ingest;
        $rootScope.currentModule = 'ingest';

        this.fetchItems = function(criteria) {
            api.ingest.query(criteria).then(function(items) {
                $scope.items = items;
            });
        };

        var update = angular.bind(this, function searchUpdated() {
            var query = this.getQuery($location.search());
            this.fetchItems({source: query});
        });

        $scope.$on('ingest:update', update);
        $scope.$watchCollection(function getSearchWithoutId() {
            return _.omit($location.search(), '_id');
        }, update);
    }

    return IngestListController;
});
