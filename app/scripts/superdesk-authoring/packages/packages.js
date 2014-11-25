(function() {

    'use strict';

    PackagesService.$inject = ['api', '$q'];
    function PackagesService(api, $q) {

    }

    PackagesCtrl.$inject = ['$scope', 'packagesService'];
    function PackagesCtrl($scope, packagesService) {

    }

    angular.module('superdesk.authoring.packages', ['superdesk.authoring.widgets', 'superdesk.api'])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
        .widget('packages', {
            icon: 'package',
            label: gettext('Packages'),
            template: 'scripts/superdesk-authoring/packages/views/packages-widget.html',
            side: 'right'
        });
    }])

    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('packages', {
            type: 'http',
            backend: {rel: 'packages'}
        });
    }])

    .controller('PackagesWidgetCtrl', PackagesCtrl)
    .service('packagesService', PackagesService);

})();
