/**
 * This file is part of Superdesk.
 *
 * Copyright 2013, 2014 Sourcefabric z.u. and contributors.
 *
 * For the full copyright and license information, please see the
 * AUTHORS and LICENSE files distributed with this source code, or
 * at https://www.sourcefabric.org/superdesk/license
 */

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

        this.addGroupToPackage = function addGroupToPackage(currentPackage, groupId) {
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

    PackagingCtrl.$inject = ['$scope', 'packagesService', 'superdesk', '$route', 'api', 'search'];
    function PackagingCtrl($scope, packagesService, superdesk, $route, api, search) {

        function fetchItem() {
            packagesService.fetch($route.current.params._id).
                then(function(fetched_package) {
                $scope.item = fetched_package;
            });
        }

        function fetchContentItems(q) {
            var query = search.query(q || null);
            query.size(20);
            api.archive.query(query.getCriteria(true))
            .then(function(result) {
                $scope.contentItems = result._items;
            });
        }

        $scope.createGroup = function() {
            superdesk.intent('create', 'group').then(function(group_name) {
                packagesService.addGroupToPackage($scope.item, group_name)
                .then(function(updatedPackage) {
                    $scope.item = updatedPackage;
                });
            });
        };

        $scope.addToFirstGroup = function addToFirstGroup(item) {
            packagesService.addItemsToPackage($scope.item, [item], $scope.item.groups[0])
            .then(function(updatedPackage) {
                $scope.item = updatedPackage;
            });
        };

        $scope.refresh = function(form) {
            fetchContentItems(form.query);
        };

        fetchItem();
        fetchContentItems();
    }

    CreateGroupCtrl.$inject = ['$scope', 'api'];
    function CreateGroupCtrl($scope) {
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
            cssClass: 'mini-modal package-group-modal',
            controller: CreateGroupCtrl,
            templateUrl: 'scripts/superdesk-packaging/views/create-group.html',
            filters: [{action: 'create', type: 'group'}]
        })
        .activity('addto.package', {
            label: gettext('Add to package'),
            controller: ['data', '$location', 'superdesk', function(data, $location, superdesk) {
                superdesk.intent('author', 'package', data.item);
            }],
            filters: [{action: 'addto', type: 'package'}],
            icon: 'plus-small'
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
