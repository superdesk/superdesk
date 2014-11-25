(function() {

    'use strict';

    PackagesService.$inject = ['api', '$q'];
    function PackagesService(api, $q) {

    }

    PackagesCtrl.$inject = ['$scope', 'packagesService', 'superdesk'];
    function PackagesCtrl($scope, packagesService, superdesk) {

        $scope.itemTypes = [
            {
                name: 'text',
                label: 'Story'
            },
            {
                name: 'picture',
                label: 'Image'
            },
            {
                name: 'video',
                label: 'Video'
            },
            {
                name: 'audio',
                label: 'Audio'
            }
        ];

        $scope.create = function(type) {
            superdesk.intent('create', 'package', {type: type}).then(function(val) {
                //do the things in the sidebar when modal get closed
            });
        };
    }

    AddToPackageController.$inject = ['$scope', 'api'];
    function AddToPackageController($scope, api) {

        api.archive.query().then(function(result) {
            $scope.items = result;
        });

        $scope.cancel = function() {
            $scope.reject();
        };

        $scope.save = function() {
            //do the saving
            $scope.resolve();
        };

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

    .config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('create.package', {
                label: gettext('Create package'),
                modal: true,
                cssClass: 'create-package-modal responsive-popup',
                controller: AddToPackageController,
                templateUrl: 'scripts/superdesk-authoring/packages/views/create-package-modal.html',
                filters: [{action: 'create', type: 'package'}]
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
