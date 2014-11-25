(function() {

    'use strict';

    PackagesService.$inject = ['api', '$log', '$q'];
    function PackagesService(api, $log, $q) {
        this.item_package = null;

        this.fetch = function(item) {
            if (item.linked_in_packages == null){
                $log.info('PackageService.fetch(), item not included in any package, item: ' + item);
                this.item_package = null;
                return $q.when(null);
            }
            var id = item.linked_in_packages[0]['package'];
            return api.find('packages', id).then(angular.bind(this, function(result) {
                this.item_package = result;
                return $q.when(result);
            }));
        };

        this.save = function(new_package) {
            return api.packages.save(new_package);
        };

        this.createPackageFromItem = function createPackageFromItem(item) {
            var new_package = {
                headline: item.headline || '',
                slugline: item.slugline || '',
                description: item.description || '',
                groups: [
                    {
                    role: 'grpRole:NEP',
                    refs: [{idRef: 'main'}],
                    id: 'root'
                },
                {
                    refs: [
                        {
                        headline: item.headline || '',
                        residRef: '/archive/' + item._id,
                        slugline: item.slugline || ''
                    }
                    ],
                    id: 'main',
                    role: 'grpRole:Main'
                }
                ]
            };

            return this.save(new_package);
        };
    }

    PackagesCtrl.$inject = ['$scope', 'packagesService', 'superdesk'];
    function PackagesCtrl($scope, packagesService, superdesk) {
        $scope.selected = {};
        $scope.$watch('item._id', reload);

        $scope.itemTypes = [
            {
                name: 'text',
                label: 'Story'
            },
            {
                name: 'text',
                label: 'Sidebar'
            },
            {
                name: 'text',
                label: 'Fact box'
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
            if ($scope.item_package == null) {
                packagesService.createPackageFromItem($scope.item)
                .then(function(new_package) {
                    $scope.selected.preview = new_package;
                    superdesk.intent('create', 'package', {type: type}).then(function(val) {
                        //do the things in the sidebar when modal get closed
                    });
                });
            } else {
                superdesk.intent('create', 'package', {type: type}).then(function(val) {
                    //do the things in the sidebar when modal get closed
                });
            }
        };

        function reload() {
            if ($scope.item) {
                packagesService.fetch($scope.item).then(function() {
                    $scope.selected.preview = packagesService.item_package;
                });
            }
        }

        reload();
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
