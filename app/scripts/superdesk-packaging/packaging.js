(function() {

    'use strict';

    PackagesService.$inject = ['api', '$q'];
    function PackagesService(api, $q) {

        this.fetch = function(packageId) {
            return api.find('packages', packageId).then(angular.bind(this, function(result) {
                return $q.when(result);
            }));
        };

        this.getGroupFor = function (item, idRef) {
            var refs = [];
            if (item) {
                refs.push({
                    headline: item.headline || '',
                    residRef: item._id,
                    location: 'archive',
                    slugline: item.slugline || '',
                    renditions: item.renditions || {}
                });
            }
            return {
                refs: refs,
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

        this.createPackageFromItems = function createPackageFromItems(items) {
            var self = this;
            var idRef = 'main';
            var item = items[0];
            var new_package = {
                headline: item.headline || item.description || '',
                slugline: item.slugline || '',
                description: item.description || '',
                state: 'draft'
            };
            var groups = [{
                role: 'grpRole:NEP',
                refs: [{idRef: idRef}],
                id: 'root'
            }];
            _.forEach(items, function(item) {
                groups.push(self.getGroupFor(item, idRef));
            });

            new_package.groups = groups;
            return api.packages.save(new_package);
        };

        this.createEmptyPackage = function createEmptyPackage() {
            var idRef = 'main';
            var new_package = {
                headline: '',
                slugline: '',
                description: '',
                groups: [
                    {
                    role: 'grpRole:NEP',
                    refs: [{idRef: idRef}],
                    id: 'root'
                },
                this.getGroupFor(null, idRef)
                ]
            };

            return api.packages.save(new_package);
        };

        this.addItemsToPackage = function addToPackage(currentPackage, items, groupId) {
            var self = this;

            var patch = _.pick(currentPackage, 'groups');
            var targetGroup = _.find(patch.groups, function(group) { return group.id === groupId; });
            _.forEach(items, function(item) {
                targetGroup.push(self.getReferenceFor(item));
            });
            return api.packages.save(currentPackage, patch);
        };

        this.addGroupToPackge = function addGroupToPackage(currentPackage, groupId) {
            var self = this;

            var patch = _.pick(currentPackage, 'groups');
            var rootGroup = _.find(patch.groups, function(group) { return group.id === 'root'; });
            var newId = self.generateNewId(rootGroup.refs, groupId);
            rootGroup.refs.push({idRef: newId});
            patch.groups.push({
                refs: [],
                id: newId,
                role: 'grpRole:' + newId
            });
            return api.packages.save(currentPackage, patch);
        };

        this.generateNewId = function generateNewId(refs, idRef) {
            var filter = function(ref) { return (ref.idRef.toLowerCase().indexOf(idRef.toLowerCase())) === 0 ? 'found' : 'none'; };
            var counts = _.countBy(refs, filter);
            return counts.found ? (idRef + '-' + counts.found) : idRef;
        };
    }

    PackagingCtrl.$inject = ['$scope', 'packagesService', 'superdesk', '$route'];
    function PackagingCtrl($scope, packagesService, superdesk, $route) {
        $scope.selected = {};
        $scope.item = null;
        $scope.selected.hide_menu = true;
        $scope.selected.hide_header = true;
        $scope.contenttab = true;

        function fetch() {
            packagesService.fetch($route.current.params._id).
                then(function(fetched_package) {
                $scope.selected.preview = fetched_package;
                $scope.item = fetched_package;
            });
        }

        $scope.createGroup = function() {
            superdesk.intent('create', 'group').then(function(group_name) {
                packagesService.addGroupToPackge($scope.selected.preview, group_name)
                .then(function(updatedPackage) {
                    $scope.selected.preview = updatedPackage;
                    $scope.item = updatedPackage;
                });
            });
        };

        fetch();
    }

    CreateGroupCtrl.$inject = ['$scope', 'api'];
    function CreateGroupCtrl($scope) {
        $scope.group_name = null;

        $scope.cancel = function() {
            $scope.reject();
        };

        $scope.save = function saveGroup(name) {
            $scope.resolve(name);
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
        .activity('create.package', {
            label: gettext('Create package'),
            controller: ['data', '$location', 'packagesService', 'superdesk', function(data, $location, packagesService, superdesk) {
                if (data) {
                    packagesService.createPackageFromItems(data.items).then(
                        function(new_package) {
                        superdesk.intent('author', 'package', new_package);
                    });
                } else {
                    packagesService.createEmptyPackage().then(
                        function(new_package) {
                        superdesk.intent('author', 'package', new_package);
                    });
                }
            }],
            filters: [
                {action: 'create', type: 'package'}
            ]
        })
        .activity('packaging', {
            when: '/packaging/:_id',
            label: gettext('Packaging'),
            templateUrl: 'scripts/superdesk-packaging/views/packaging.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            controller: PackagingCtrl,
            filters: [{action: 'author', type: 'package'}]
        })
        .activity('edit.package', {
            label: gettext('Edit package'),
            priority: 10,
            icon: 'pencil',
            controller: ['data', '$location', 'superdesk', function(data, $location, superdesk) {
                superdesk.intent('author', 'package', data.item);
            }],
            filters: [
                {action: 'list', type: 'archive'}
            ],
            condition: function(item) {
                return item.type === 'composite';
            }
        })
        .activity('create.group', {
            label: gettext('Create new group'),
            modal: true,
            cssClass: 'create-group-modal responsive-popup',
            controller: CreateGroupCtrl,
            templateUrl: 'scripts/superdesk-packaging/views/create-group.html',
            filters: [{action: 'create', type: 'group'}]
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
