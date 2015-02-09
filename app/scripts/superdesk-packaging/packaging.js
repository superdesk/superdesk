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
        var currentPackage = null;

        this.fetch = function(packageId) {
            return api.find('packages', packageId).then(function(result) {
                currentPackage = result;
                return result;
            });
        };

        function getGroupFor(item, idRef) {
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
        }

        function getReferenceFor(item) {
            return {
                headline: item.headline || '',
                residRef: item._id,
                location: 'archive',
                slugline: item.slugline || '',
                renditions: item.renditions || {}
            };
        }

        function setDefaults(item, defaults) {
            if (_.isObject(defaults)) {
                return _.merge(item, defaults);
            }
            return item;
        }

        this.createPackageFromItems = function createPackageFromItems(items, defaults) {
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
                groups.push(getGroupFor(item, idRef));
            });
            new_package = setDefaults(new_package, defaults);

            new_package.groups = groups;
            return api.packages.save(new_package);
        };

        this.createEmptyPackage = function createEmptyPackage(defaults) {
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
                getGroupFor(null, idRef)
                ]
            };
            new_package = setDefaults(new_package, defaults);

            return api.packages.save(new_package);
        };

        this.addItemsToPackage = function addToPackage(items, groupId) {
            var patch = {groups: _.cloneDeep(currentPackage.groups)};
            var targetGroup = _.find(patch.groups, function(group) { return group.id.toLowerCase() === groupId.toLowerCase(); });

            if (!targetGroup) {
                var rootGroup = _.find(patch.groups, function(group) { return group.id === 'root'; });
                rootGroup.refs.push({idRef: groupId});
                targetGroup = {
                    refs: [],
                    id: groupId,
                    role: 'grpRole:' + groupId
                };
                patch.groups.push(targetGroup);
            }
            _.forEach(items, function(item) {
                targetGroup.refs.push(getReferenceFor(item));
            });
            return api.packages.save(currentPackage, patch);
        };

        this.removeItem = function removeItem(item) {
            var patch = {groups: _.cloneDeep(currentPackage.groups)};

            _.forEach(patch.groups, function(group) {
                _.remove(group.refs, function(ref_item) {
                    return ref_item.guid === item.guid;
                });
            });
            _.remove(patch.groups, function(group) {
                return group.id !== 'root' && group.refs.length === 0;
            });

            var rootGroup = _.find(patch.groups, function(group) { return group.id === 'root'; });
            rootGroup.refs = [];
            _.forEach(patch.groups, function(group) {
                if (group.id !== 'root') {
                    rootGroup.refs.push({idRef: group.id});
                }
            });
            return api.packages.save(currentPackage, patch);
        };
    }

    PackagingCtrl.$inject = ['$scope', 'packagesService', 'superdesk', '$route', 'api', 'search', 'lock', 'ContentCtrl'];
    function PackagingCtrl($scope, packagesService, superdesk, $route, api, search, lock, ContentCtrl) {

        $scope.widget_target = 'packages';
        $scope.content = new ContentCtrl($scope);

        function fetchItem() {
            packagesService.fetch($route.current.params._id).
                then(function(fetched_package) {
                $scope.item = fetched_package;
                lock.lock($scope.item);
            });
        }

        $scope.remove = function removeItem(obj) {
            packagesService.removeItem(obj.item);
        };

        $scope.close = function closePackage() {
            lock.unlock($scope.item);
        };

        fetchItem();
    }

    SearchWidgetCtrl.$inject = ['$scope', 'packagesService', 'api', 'search'];
    function SearchWidgetCtrl($scope, packagesService, api, search) {

        $scope.selected = null;
        var packageItems = null;

        $scope.itemTypes = [
            {
                icon: 'text',
                label: 'Main'
            },
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
            }
        ];

        function fetchContentItems(q) {
            var query = search.query(q || null);
            query.size(25);
            api.archive.query(query.getCriteria(true))
            .then(function(result) {
                $scope.contentItems = result._items;
            });
        }

        $scope.$watch('query', function(query) {
            fetchContentItems(query);
        });

        $scope.$watch('item.groups', function() {
            getPackageItems();
        }, true);

        $scope.addItemToGroup = function addItemsToGroup(groupId, item) {
            packagesService.addItemsToPackage([item], groupId.label.toLowerCase())
            .then(function() {
                getPackageItems();
            });
        };

        fetchContentItems();

        $scope.preview = function(item) {
            $scope.selected = item;
        };

        function getPackageItems() {
            var items = [];
            if ($scope.item.groups) {
                _.each($scope.item.groups, function(group) {
                    if (group.id !== 'root') {
                        _.each(group.refs, function(item) {
                            items.push(item.guid);
                        });
                    }
                });
            }
            packageItems = items;
        }

        $scope.itemInPackage = function(item) {
            return _.indexOf(packageItems, item.guid) > -1;
        };
    }

    function PreventPreviewDirective() {
        return {
            link: function(scope, el) {
                el.bind('click', previewOnClick);

                scope.$on('$destroy', function() {
                    el.unbind('click', previewOnClick);
                });

                function previewOnClick(event) {
                    if ($(event.target).closest('.group-select').length === 0) {
                        scope.$apply(function() {
                            scope.preview(scope.pitem);
                        });
                    }
                }
            }
        };
    }

    var app = angular.module('superdesk.packaging', [
        'superdesk.activity',
        'superdesk.api'
    ]);

    app
    .service('packagesService', PackagesService)
    .directive('sdWidgetPreventPreview', PreventPreviewDirective)
    .config(['superdeskProvider', function(superdesk) {
        superdesk
        .activity('create.package', {
            label: gettext('Create package'),
            controller: ['data', 'packagesService', 'superdesk',
                function(data, packagesService, superdesk) {
                    if (data && data.items) {
                        packagesService.createPackageFromItems(data.items, data.defaults).then(
                            function(new_package) {
                            superdesk.intent('author', 'package', new_package);
                        });
                    } else {
                        var defaultData = data && data.defaults ? data.defaults : {};
                        packagesService.createEmptyPackage(defaultData).then(
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
            href: '/packaging/:_id',
            label: gettext('Packaging'),
            templateUrl: 'scripts/superdesk-packaging/views/packaging.html',
            topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
            controller: PackagingCtrl,
            filters: [{action: 'author', type: 'package'}]
        })
        .activity('edit.package', {
            label: gettext('Edit package'),
            href: '/packaging/:_id',
            priority: 10,
            icon: 'pencil',
            controller: ['data', 'superdesk', function(data, superdesk) {
                superdesk.intent('author', 'package', data.item);
            }],
            filters: [
                {action: 'list', type: 'archive'}
            ],
            condition: function(item) {
                return item.type === 'composite';
            }
        })
        .activity('package.item', {
            label: gettext('Package item'),
            priority: 5,
            icon: 'package-plus',
            controller: ['data', 'packagesService', 'superdesk', function(data, packagesService, superdesk) {
                packagesService.createPackageFromItems([data.item]).then(function(new_package) {
                        superdesk.intent('author', 'package', new_package);
                    });
            }],
            filters: [
                {action: 'list', type: 'archive'}
            ]
        });

    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('packages', {
            type: 'http',
            backend: {rel: 'packages'}
        });
    }])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('search', {
                icon: 'view',
                label: gettext('Search'),
                template: 'scripts/superdesk-packaging/views/search.html',
                side: 'left',
                extended: true,
                display: {authoring: false, packages: true}
            });
    }])
    .controller('SearchWidgetCtrl', SearchWidgetCtrl);

    return app;
})();
