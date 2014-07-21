define([
    'lodash',
    'superdesk-archive/controllers/baseList'
], function(_, BaseListController) {
    'use strict';

    IngestListController.$inject = ['$scope', '$injector', 'api', '$rootScope'];
    function IngestListController($scope, $injector, api, $rootScope) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.type = 'ingest';
        $scope.api = api.ingest;

        $rootScope.currentModule = 'ingest';

        this.fetchItems = function(criteria) {
            api.ingest.query(criteria).then(function(items) {
                $scope.items = items;
            });
        };
    }

    return IngestListController;
});
