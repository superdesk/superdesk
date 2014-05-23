define([
    'lodash',
    '../../superdesk-archive/controllers/baseList'
], function(_, BaseListController) {
    'use strict';

    IngestListController.$inject = ['$scope', '$injector', 'api'];
    function IngestListController($scope, $injector, api) {
        $injector.invoke(BaseListController, this, {$scope: $scope});

        $scope.type = 'ingest';

        this.fetchItems = function(criteria) {
            api.ingest.query(criteria).then(function(items) {
                $scope.items = items;
            });
        };
    }

    return IngestListController;
});
