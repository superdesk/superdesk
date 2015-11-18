(function() {

    'use strict';

    PackagesCtrl.$inject = ['$scope', '$location', 'superdesk', 'api', 'search'];
    function PackagesCtrl($scope, $location, superdesk, api, search) {
        $scope.contentItems = [];

        function fetchPackages() {
            var query = search.query();
            query.clear_filters();
            var filter = [];
            _.forEach($scope.item.linked_in_packages, function(packageRef) {
                filter.push(packageRef['package']);
            });

            query.size(25).filter({'terms': {'guid': filter}});
            api.archive.query(query.getCriteria(true))
            .then(function(result) {
                $scope.contentItems = result._items;
            });
        }

        $scope.openPackage = function(packageItem) {
            superdesk.intent('edit', 'item', packageItem);
        };

        if ($scope.item && $scope.item.linked_in_packages && $scope.item.linked_in_packages.length > 0) {
            fetchPackages();
        }
    }

    return angular.module('superdesk.authoring.packages', ['superdesk.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
        .widget('packages', {
            icon: 'package',
            label: gettext('Packages'),
            template: 'scripts/superdesk-authoring/packages/views/packages-widget.html',
            order: 5,
            side: 'right',
            display: {authoring: true, packages: true, legalArchive: false}
        });
    }])
    .controller('PackagesWidgetCtrl', PackagesCtrl);

})();
