(function() {

    'use strict';

    PackagesService.$inject = ['api', '$q'];
    function PackagesService(api, $q) {

        this.fetch = function(item) {
            if (item.linked_in_packages == null) {
                return $q.when(null);
            }
            var id = item.linked_in_packages[0]['package'];
            return api.find('packages', id).then(angular.bind(this, function(result) {
                return $q.when(result);
            }));
        };

        this.getGroupFor = function (item, idRef) {
            return {
                refs: [{
                    headline: item.headline || '',
                    residRef: item._id,
                    location: 'archive',
                    slugline: item.slugline || '',
                    renditions: item.renditions || {}
                }],
                id: idRef,
                role: 'grpRole:' + idRef
            };
        };

        this.getReferenceFor = function (item) {
            return {
                headline: item.headline || '',
                residRef: item._id,
                location: 'archive',
                slugline: item.slugline || '',
                renditions: item.renditions || {}
            };
        };

        this.createPackageFromItem = function createPackageFromItem(item) {
            var idRef = 'main';
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
                this.getGroupFor(item, idRef)
                ]
            };

            return api.packages.save(new_package);
        };

        this.createEmptyPackage = function createEmptyPackage() {
            var new_package = {
                headline: '',
                slugline: '',
                description: '',
                groups: [
                    {
                    role: 'grpRole:NEP',
                    id: 'root'
                }
                ]
            };

            return api.packages.save(new_package);
        };

        this.addItemsToMainPackage = function addToPackage(currentPackage, items) {
            var self = this;
            var idRef = 'main';

            var patch = _.pick(currentPackage, 'groups');
            var mainGroup = _.find(patch.groups, function(group) { return group.id === idRef; });
            _.forEach(items, function(item) {
                mainGroup.refs.push(self.getReferenceFor(item));
            });
            return api.packages.save(currentPackage, patch);
        };

        this.addItemsToPackage = function addToPackage(currentPackage, items, groupId) {
            var self = this;

            var patch = _.pick(currentPackage, 'groups');
            var rootGroup = _.find(patch.groups, function(group) { return group.id === 'root'; });
            _.forEach(items, function(item) {
                var newId = self.generateNewId(rootGroup.refs, groupId);
                rootGroup.refs.push({idRef: newId});
                patch.groups.push(self.getGroupFor(item, newId));
            });
            return api.packages.save(currentPackage, patch);
        };

        this.generateNewId = function generateNewId(refs, idRef) {
            var filter = function(ref) { return (ref.idRef.toLowerCase().indexOf(idRef.toLowerCase())) === 0 ? 'found' : 'none'; };
            var counts = _.countBy(refs, filter);
            return counts.found ? (idRef + '-' + counts.found) : idRef;
        };
    }

    PackagingCtrl.$inject = ['$scope', 'packagesService', 'superdesk'];
    function PackagingCtrl($scope, packagesService, superdesk) {
        $scope.selected = {};
        $scope.selected.hide_menu = true;
        $scope.contenttab = true;

        $scope.itemTypes = [
            {
            icon: 'text',
            label: 'Story'
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

        this.edit = function(item) {
            $scope.selected.preview = item;
        };

        $scope.create = function(item) {
            packagesService.createPackageFromItem(item)
            .then(function(new_package) {
                $scope.selected.preview = new_package;
            });
        };
        $scope.createEmpty = function createEmptyPackage() {
            packagesService.createEmptyPackage()
            .then(function(new_package) {
                $scope.selected.preview = new_package;
            });
        };

        $scope.append = function(type) {
            superdesk.intent('append', 'package', {type: type.icon}).then(function(items) {
                packagesService.addItemsToMainPackage($scope.selected.preview, items)
                .then(function(updatedPackage) {
                    $scope.selected.preview = updatedPackage;
                });
            });
        };
    }

    AddToPackageCtrl.$inject = ['$scope', 'api'];
    function AddToPackageCtrl($scope, api) {

        $scope.selectedList = [];

        api.archive.query().then(function(result) {
            $scope.items = result;
        });

        $scope.isInSelectedList = function(item) {
            return _.findIndex($scope.selectedList, {_id: item._id}) !== -1;
        };

        $scope.cancel = function() {
            $scope.reject();
        };

        $scope.save = function() {
            //TODO: make the selection work
            //var selected = _.sample($scope.items._items);
            $scope.resolve($scope.selectedList);
        };
    }

    var app = angular.module('superdesk.packaging', [
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
    .service('packagesService', PackagesService)
    .config(['superdeskProvider', function(superdesk) {
        superdesk
        .activity('packaging', {
            label: gettext('Packaging'),
            templateUrl: 'scripts/superdesk-packaging/views/packaging.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            controller: PackagingCtrl,
            filters: [{action: 'author', type: 'package'}],
            resolve: {
                item: ['$route', 'packaging', function($route, packaging) {
                    return packaging.create($route.current.params._id);
                }]
            }
        })
        .activity('append.package', {
            label: gettext('Add items to package'),
            modal: true,
            cssClass: 'create-package-modal responsive-popup',
            controller: AddToPackageCtrl,
            templateUrl: 'scripts/superdesk-packaging/packages/views/create-package-modal.html',
            filters: [{action: 'append', type: 'package'}]
        });
    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('packages', {
            type: 'http',
            backend: {rel: 'packages'}
        });
    }]);

    return app;
})();
