(function() {

    'use strict';

    PackagesService.$inject = ['api', '$log', '$q'];
    function PackagesService(api, $log, $q) {

        this.fetch = function(item) {
            if (item.linked_in_packages == null) {
                $log.info('PackageService.fetch(), item not included in any package, item: ' + item);
                return $q.when(null);
            }
            var id = item.linked_in_packages[0]['package'];
            return api.find('packages', id).then(angular.bind(this, function(result) {
                return $q.when(result);
            }));
        };

        this.createPackageFromItem = function createPackageFromItem(item, idRef) {
            var new_package = {
                headline: item.headline || '',
                slugline: item.slugline || '',
                description: item.description || '',
                groups: [
                    {
                    role: 'grpRole:NEP',
                    refs: [{idRef: idRef}],
                    id: 'root'
                },
                {
                    refs: [{
                        headline: item.headline || '',
                        residRef: item._id,
                        location: 'archive',
                        slugline: item.slugline || '',
                        renditions: item.renditions
                    }],
                    id: idRef,
                    role: 'grpRole:Main'
                }]
            };

            return api.packages.save(new_package);
        };

        this.addItemToPackage = function addToPackage(currentPackage, item, idRef) {
            var patch = _.pick(currentPackage, 'groups');
            var rootGroup = _.find(patch.groups, function(group) { return group.id === 'root'; });
            var newId = this.generateNewId(rootGroup.refs, idRef);
            rootGroup.refs.push({idRef: newId});
            patch.groups.push({
                    refs: [{
                        headline: item.headline || '',
                        residRef: item._id,
                        location: 'archive',
                        slugline: item.slugline || '',
                        renditions: item.renditions
                    }],
                    id: newId,
                    role: 'grpRole:' + newId
                });
            return api.packages.save(currentPackage, patch);
        };

        this.generateNewId = function generateNewId(refs, idRef) {
            var filter = function(ref) { return (ref.idRef.toLowerCase().indexOf(idRef.toLowerCase())) === 0 ? 'found' : 'none'; };
            var counts = _.countBy(refs, filter);
            return idRef + '-' + counts.found;
        };
    }

    PackagesCtrl.$inject = ['$scope', 'packagesService', 'superdesk'];
    function PackagesCtrl($scope, packagesService, superdesk) {
        $scope.selected = {};
        $scope.selected.hide_menu = true;
        $scope.contenttab = true;
        $scope.$watch('item._id', reload);

        $scope.itemTypes = [
            {
                icon: 'text',
                label: 'Story'
            },
            {
                icon: 'text',
                label: 'Sidebar'
            },
            {
                icon: 'text',
                label: 'Fact box'
            },
            {
                icon: 'picture',
                label: 'Image'
            },
            {
                icon: 'video',
                label: 'Video'
            },
            {
                icon: 'audio',
                label: 'Audio'
            }
        ];

        $scope.create = function(type) {
            if ($scope.selected.preview == null) {
                packagesService.createPackageFromItem($scope.item, type.label)
                .then(function(new_package) {
                    $scope.selected.preview = new_package;
                });
            } else {
                superdesk.intent('create', 'package', {type: type.icon}).then(function(val) {
                    console.log(val);
                    packagesService.addItemToPackage($scope.selected.preview, val, type.label)
                    .then(function(updatedPackage) {
                        $scope.selected.preview = updatedPackage;
                    });
                });
            }
        };

        function reload() {
            if ($scope.item) {
                if ($scope.item.type === 'composite'){
                    $scope.selected.preview = $scope.item;
                } else {
                    packagesService.fetch($scope.item).then(function(item_package) {
                        $scope.selected.preview = item_package;
                    });
                }
            }
        }
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
            //TODO: make the selection work
            var selected = _.sample($scope.items._items);
            $scope.resolve(selected);
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
