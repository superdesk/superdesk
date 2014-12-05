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
                packagesService.createPackageFromItem($scope.item)
                .then(function(new_package) {
                    $scope.selected.preview = new_package;
                });
            } else {
                superdesk.intent('create', 'package', {type: type.icon}).then(function(items) {
                    packagesService.addItemsToMainPackage($scope.selected.preview, items)
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
