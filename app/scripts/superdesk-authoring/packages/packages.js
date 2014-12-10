(function() {

    'use strict';

    PackagesCtrl.$inject = ['$scope', 'superdesk'];
    function PackagesCtrl($scope, superdesk) {
        $scope.contenttab = true;

        $scope.create = function() {
            superdesk.intent('create', 'package', {item: $scope.item});
        };
    }

    return angular.module('superdesk.authoring.packages', ['superdesk.authoring.widgets'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
        .widget('packages', {
            icon: 'package',
            label: gettext('Packages'),
            template: 'scripts/superdesk-authoring/packages/views/packages-widget.html',
            side: 'right'
        });
    }])
    .controller('PackagesWidgetCtrl', PackagesCtrl);

})();
