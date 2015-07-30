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

    PackagesService.$inject = ['api', '$q', 'archiveService'];
    function PackagesService(api, $q, archiveService) {

        this.groupList = ['main', 'story', 'sidebars', 'fact box'];

        this.fetch = function fetch(_id) {
            return api.find('archive', _id).then(function(result) {
                return result;
            });
        };

        this.createPackageFromItems = function (items, defaults) {
            var idRef = 'main';
            var item = items[0];
            var new_package = {
                headline: item.headline || item.description || '',
                slugline: item.slugline || '',
                description: item.description || '',
                state: 'draft',
                type: 'composite'
            };
            var groups = [{
                    role: 'grpRole:NEP',
                    refs: [{idRef: idRef}],
                    id: 'root'
                },
                getGroupFor(null, idRef)
            ];
            new_package = setDefaults(new_package, defaults);
            new_package.groups = groups;
            this.addItemsToPackage(new_package, idRef, items);
            return api.archive.save(new_package);
        };

        this.createEmptyPackage = function(defaults, idRef) {
            idRef = idRef || 'main';
            var new_package = {
                headline: '',
                slugline: '',
                description: '',
                type: 'composite',
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

            return api.archive.save(new_package);

        };

        this.addItemsToPackage = function(current, group_id, items) {

            var origGroups = _.cloneDeep(current.groups);

            var targetGroup = _.find(origGroups, function(group) {
                return group.id.toLowerCase() === group_id;
            });

            if (!targetGroup) {
                var rootGroup = _.find(origGroups, {id: 'root'});
                rootGroup.refs.push({idRef: group_id});
                targetGroup = {
                    id: group_id,
                    refs: [],
                    role: 'grpRole:' + group_id
                };
                origGroups.push(targetGroup);
            }
            _.each(items, function(item) {
                targetGroup.refs.push(getReferenceFor(item));
            });
            _.extend(current, {groups: origGroups});
        };

        this.fetchItem = function(packageItem) {
            var repo = packageItem.location || 'ingest';
            return api(repo).getById(packageItem.residRef)
                .then(function(item) {
                    return item;
                }, function(response) {
                    if (response.status === 404) {
                        console.log('Item not found');
                    }
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

        function setDefaults(item, defaults) {
            if (angular.isUndefined(defaults) || !_.isObject(defaults)) {
                defaults = {};
            }

            archiveService.addTaskToArticle(defaults);
            return _.merge(item, defaults);
        }

        function getReferenceFor(item) {
            return {
                headline: item.headline || '',
                residRef: item._id,
                location: 'archive',
                slugline: item.slugline || '',
                renditions: item.renditions || {},
                itemClass: item.type ? ('icls:' + item.type) : ''
            };
        }

    }

    PackagingController.$inject = ['$scope', 'item', 'packages', 'api', 'modal', 'notify', 'gettext', 'superdesk'];
    function PackagingController($scope, item, packages, api, modal, notify, gettext, superdesk) {
        $scope.origItem = item;
        $scope.action = 'edit';

        $scope.lock = function() {
            superdesk.intent('author', 'package', item);
        };

        // Highlights related functionality

        $scope.highlight = !!item.highlight;

        $scope.exportHighlight = function(item) {
            if ($scope.save_enabled()) {
                modal.confirm(gettext('You have unsaved changes, do you want to continue.'))
                    .then(function() {
                        _exportHighlight(item._id);
                    }
                );
            } else {
                _exportHighlight(item._id);
            }
        };

        function _exportHighlight(_id) {
            api.generate_highlights.save({}, {'package': _id})
            .then(function(item) {
                superdesk.intent('author', 'article', item);
            }, function(response) {
                notify.error(gettext('Error creating highlight.'));
            });
        }
    }

    SearchWidgetCtrl.$inject = ['$scope', 'packages', 'api', 'search'];
    function SearchWidgetCtrl($scope, packages, api, search) {

        $scope.selected = null;
        $scope.multiSelected = [];
        $scope.query = null;
        $scope.highlight = null;

        var packageItems = null;
        var init = false;

        $scope.groupList = packages.groupList;

        function fetchContentItems() {
            if (!init) {
                return;
            }
            var query = search.query($scope.query);
            query.size(25);
            if ($scope.highlight) {
                query.filter({term: {'highlights': $scope.highlight.toString()}});
            }
            api.archive.query(query.getCriteria(true))
            .then(function(result) {
                $scope.contentItems = result._items;
            });
        }

        $scope.$watch('query', function(query) {
            fetchContentItems();
        });

        $scope.$watch('highlight', function(highlight) {
            fetchContentItems();
        });

        $scope.$watch('item', function(item) {
            $scope.highlight = item.highlight;
            if ($scope.highlight) {
                api('highlights').getById($scope.highlight)
                .then(function(result) {
                    $scope.groupList = result.groups;
                    init = true;
                    fetchContentItems();
                }, function(response) {
                    init = true;
                    fetchContentItems();
                });
            } else {
                init = true;
                fetchContentItems();
            }
        });

        $scope.$watch('item.groups', function() {
            getPackageItems();
        }, true);

        $scope.addItemToGroup = function(group, item) {
            packages.addItemsToPackage($scope.item, group, [item]);
            $scope.autosave($scope.item);
        };

        $scope.preview = function(item) {
            $scope.selected = item;
        };

        function getPackageItems() {
            var items = [];
            if ($scope.item.groups) {
                _.each($scope.item.groups, function(group) {
                    if (group.id !== 'root') {
                        _.each(group.refs, function(item) {
                            items.push(item.residRef);
                        });
                    }
                });
            }
            packageItems = items;
        }

        $scope.itemInPackage = function(item) {
            return _.indexOf(packageItems, item._id) > -1;
        };

        $scope.addToSelected = function(pitem) {
            if (pitem.multi) {
                $scope.multiSelected.push(pitem);
            } else {
                _.remove($scope.multiSelected, pitem);
            }
        };

        $scope.addMultiItemsToGroup = function(group) {
            //add to group
            packages.addItemsToPackage($scope.item, group, $scope.multiSelected);
            $scope.autosave($scope.item);

            //uncheck all
            _.each($scope.multiSelected, function(item) {
                item.multi = false;
            });

            //clear items
            $scope.multiSelected = [];
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

    PackageEditDirective.$inject = ['authoring'];
    function PackageEditDirective(authoring) {
        return {
            templateUrl: 'scripts/superdesk-packaging/views/sd-package-edit.html',
            link: function(scope) {
                scope.limits = authoring.limits;
                scope._editable = scope.origItem._editable;
                scope._isInPublishedStates = authoring.isPublished(scope.origItem);
            }
        };
    }

    function PackageItemsEditDirective() {
        return {
            scope: false,
            require: 'ngModel',
            templateUrl: 'scripts/superdesk-packaging/views/sd-package-items-edit.html',
            link: function(scope, elem, attrs, ngModel) {
                ngModel.$render = function() {
                    scope.list = ngModel.$viewValue;
                };

                ngModel.$parsers.unshift(function(viewValue) {
                    var groups = null;
                    if (viewValue && viewValue.list) {
                        groups = [];
                        groups.push({
                            role: 'grpRole:NEP',
                            refs: _.map(viewValue.list, function(r) {
                                return {idRef: r.id};
                            }),
                            id: 'root'
                        });
                        _.each(viewValue.list, function(l) {
                            groups.push({
                                id: l.id,
                                role: 'grpRole:' + l.id,
                                refs: l.items
                            });
                        });
                    }
                    return groups;
                });

                ngModel.$formatters.unshift(function(modelValue) {

                    var root = _.find(modelValue, {id: 'root'});
                    var firstLevelGroups = _.map(root.refs, function(group) {
                        return {
                            id: group.idRef,
                            items: []
                        };
                    });

                    _.each(firstLevelGroups, function(group) {
                        group.items = visit(group.id);
                    });

                    function visit(group_id) {
                        var _group = _.find(modelValue, {id: group_id});
                        var items = [];
                        _.each(_group.refs, function(ref) {
                            if (_isNode(ref)) {
                                items = _.union(items, visit(ref.idRef));
                            } else {
                                items.push(ref);
                            }
                        });
                        return items;
                    }

                    function _isNode(obj) {
                        return angular.isDefined(obj.idRef);
                    }

                    return firstLevelGroups;
                });

                scope.remove = function(group_id, residRef) {
                    var group = _.find(scope.list, {id: group_id});
                    _.remove(group.items, {residRef: residRef});
                    autosave();
                };

                scope.reorder = function(start, end) {
                    var src = _.find(scope.list, {id: start.group});
                    var dest = _.find(scope.list, {id: end.group});
                    if (start.index !== end.index || start.group !== end.group) {
                        dest.items.splice(end.index, 0, src.items.splice(start.index, 1)[0]);
                    } else {
                        //just change the address
                        dest.items = _.cloneDeep(dest.items);
                    }
                    autosave();
                };

                function autosave() {
                    ngModel.$setViewValue({list: scope.list});
                    scope.autosave(scope.item);
                }
            }
        };
    }

    function SortPackageItemsDirective() {
        return {
            link: function(scope, element) {

                var updated = false;

                element.sortable({
                    items: '.package-edit-items li',
                    cursor: 'move',
                    containment: '.package-edit-container',
                    tolerance: 'pointer',
                    placeholder: {
                        element: function(current) {
                            var height = current.height() - 40;
                            return $('<li class="placeholder" style="height:' + height + 'px"></li>')[0];
                        },
                        update: function() {
                            return;
                        }
                    },
                    start: function(event, ui) {
                        ui.item.data('start_index', ui.item.parent().find('li.sort-item').index(ui.item));
                        ui.item.data('start_group', ui.item.parent().data('group'));
                    },
                    stop: function(event, ui) {
                        if (updated) {
                            updated = false;
                            var start = {
                                index: ui.item.data('start_index'),
                                group: ui.item.data('start_group')
                            };
                            var end = {
                                index: ui.item.parent().find('li.sort-item').index(ui.item),
                                group: ui.item.parent().data('group')
                            };
                            ui.item.remove();
                            scope.reorder(start, end);
                            scope.$apply();
                        }
                    },
                    update: function(event, ui) {
                        updated = true;
                    },
                    cancel: '.fake'
                });
            }
        };
    }

    PackageItemPreviewDirective.$inject = ['api', 'lock'];
    function PackageItemPreviewDirective(api, lock) {
        return {
            templateUrl: 'scripts/superdesk-packaging/views/sd-package-item-preview.html',
            link: function(scope) {
                scope.data = null;
                scope.error = null;

                if (scope.item.location) {
                    api[scope.item.location].getById(scope.item.residRef)
                    .then(function(result) {
                        scope.data = result;
                        scope.isLocked = lock.isLocked(scope.data);
                        scope.isPublished = scope.data.state === 'published';
                    }, function(response) {
                        scope.error = true;
                    });
                }

                scope.$on('item:lock', function(_e, data) {
                    if (scope.data && scope.data._id === data.item) {
                        scope.$applyAsync(function() {
                            scope.data.lock_user = data.user;
                            scope.isLocked = lock.isLocked(scope.data);
                        });
                    }
                });

                scope.$on('item:unlock', function(_e, data) {
                    if (scope.data && scope.data._id === data.item) {
                        scope.$applyAsync(function() {
                            scope.data.lock_user = null;
                            scope.isLocked = false;
                        });
                    }
                });

                scope.$on('item:publish', function(_e, data) {
                    if (scope.data && scope.data._id === data.item) {
                        scope.$applyAsync(function() {
                            scope.isPublished = true;
                        });
                    }
                });
            }
        };
    }

    function PackageDirective() {
        var solveRefs = function(item, groups) {
            var items = {childId: '_items', childData: []};
            var tree = [items];
            _.each(item.refs, function(ref) {
                if (ref.idRef) {
                    tree.push({childId: ref.idRef, childData: solveRefs(_.find(groups, {id: ref.idRef}), groups)});
                } else if (ref.residRef) {
                    items.childData.push(ref);
                }
            });
            return tree;
        };

        return {
            templateUrl: 'scripts/superdesk-packaging/views/sd-package.html',
            scope: {
                item: '=',
                setitem: '&'
            },
            link: function(scope, elem, attrs) {
                scope.mode = attrs.mode || 'tree';
                scope.$watchGroup(['item', 'item.groups'], function() {
                    if (scope.item && scope.item.groups) {
                        scope.tree = solveRefs(
                            _.find(scope.item.groups, {id: 'root'}),
                            scope.item.groups
                        );
                    }
                });
            }
        };
    }

    function PackageItemDirective() {
        return {
            templateUrl: 'scripts/superdesk-packaging/views/sd-package-item.html',
            scope: {
                id: '=',
                item: '=',
                setitem: '&',
                mode: '='
            },
            link: function(scope, elem) {
            }
        };
    }

    PackageItemProxyDirective.$inject = ['$compile'];
    function PackageItemProxyDirective($compile) {
        var template =
            '<div sd-package-item data-id="id"' +
                ' data-item="item"' +
                ' data-setitem="setitem({selected: selected})"' +
                ' data-mode="mode">' +
            '</div>';

        return {
            scope: {
                id: '=',
                item: '=',
                setitem: '&',
                mode: '='
            },
            link: function(scope, elem) {
                elem.append($compile(template)(scope));
            }
        };
    }

    PackageRefDirective.$inject = ['api', '$rootScope'];
    function PackageRefDirective(api, $rootScope) {
        return {
            templateUrl: 'scripts/superdesk-packaging/views/sd-package-ref.html',
            scope: {
                item: '=',
                setitem: '&'
            }
        };
    }

    var app = angular.module('superdesk.packaging', [
        'superdesk.activity',
        'superdesk.api',
        'superdesk.authoring'
    ]);

    app
    .service('packages', PackagesService)
    .directive('sdPackageEdit', PackageEditDirective)
    .directive('sdPackageItemsEdit', PackageItemsEditDirective)
    .directive('sdSortPackageItems', SortPackageItemsDirective)
    .directive('sdPackage', PackageDirective)
    .directive('sdPackageItem', PackageItemDirective)
    .directive('sdPackageItemProxy', PackageItemProxyDirective)
    .directive('sdPackageRef', PackageRefDirective)
    .directive('sdPackageItemPreview', PackageItemPreviewDirective)
    .directive('sdWidgetPreventPreview', PreventPreviewDirective)

    .config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('packaging', {
                category: '/authoring',
                href: '/packaging/:_id',
                when: '/packaging/:_id',
                label: gettext('Packaging'),
                templateUrl: 'scripts/superdesk-packaging/views/packaging.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
                controller: PackagingController,
                filters: [{action: 'author', type: 'package'}],
                resolve: {
                    item: ['$route', 'authoring', function($route, authoring) {
                        return authoring.open($route.current.params._id, false);
                    }]
                },
                authoring: true
            })
            .activity('edit.package', {
                label: gettext('Edit package'),
                href: '/packaging/:_id',
                priority: 10,
                icon: 'pencil',
                controller: ['data', 'superdesk', function(data, superdesk) {
                    superdesk.intent('author', 'package', data.item);
                }],
                filters: [{action: 'list', type: 'archive'}],
                condition: function(item) {
                    return !_.contains(['published', 'killed', 'corrected'], item.state) &&
                        item.type === 'composite' && item.package_type !== 'takes';
                },
                additionalCondition:['authoring', 'item', function(authoring, item) {
                    return authoring.itemActions(item).package_item;
                }]
            })
            .activity('view.package', {
                label: gettext('View item'),
                priority: 2000,
                icon: 'external',
                controller: ['data', 'superdesk', function(data, superdesk) {
                    superdesk.intent('read_only', 'content_package', data.item);
                }],
                filters: [{action: 'list', type: 'archive'}],
                condition: function(item) {
                    return item.type === 'composite';
                }
            })
            .activity('read_only.content_package', {
                category: '/packaging',
                href: '/packaging/:_id/view',
                when: '/packaging/:_id/view',
                label: gettext('Packaging Read Only'),
                templateUrl: 'scripts/superdesk-packaging/views/packaging.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                sideTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-sidenav.html',
                controller: PackagingController,
                filters: [{action: 'read_only', type: 'content_package'}],
                resolve: {
                    item: ['$route', 'authoring', function($route, authoring) {
                        return authoring.open($route.current.params._id, true);
                    }]
                },
                authoring: true
            })
            .activity('create.package', {
                label: gettext('Create package'),
                controller: ['data', 'packages', 'superdesk',
                    function(data, packages, superdesk) {
                        if (data && data.items) {
                            packages.createPackageFromItems(data.items, data.defaults)
                            .then(function(new_package) {
                                superdesk.intent('author', 'package', new_package);
                            });
                        } else {
                            var defaultData = data && data.defaults ? data.defaults : {};
                            packages.createEmptyPackage(defaultData)
                            .then(function(new_package) {
                                superdesk.intent('author', 'package', new_package);
                            });
                        }
                    }],
                filters: [{action: 'create', type: 'package'}],
                condition: function(item) {
                    return item ? item.state !== 'killed' && item.package_type !== 'takes' : true;
                }
            })
            .activity('packageitem', {
                label: gettext('Package item'),
                priority: 5,
                icon: 'package-plus',
                controller: ['data', 'packages', 'superdesk', 'notify', 'gettext', function(data, packages, superdesk, notify, gettext) {
                    packages.createPackageFromItems([data.item])
                    .then(function(new_package) {
                        superdesk.intent('author', 'package', new_package);
                    }, function(response) {
                        if (response.status === 403 && response.data && response.data._message) {
                            notify.error(gettext(response.data._message), 3000);
                        }
                    });
                }],
                filters: [
                    {action: 'list', type: 'archive'}
                ],
                additionalCondition:['authoring', 'item', function(authoring, item) {
                    return authoring.itemActions(item).package_item;
                }],
                group: 'packaging'
            });
    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('archive', {
            type: 'http',
            backend: {rel: 'archive'}
        });
    }])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('search', {
                icon: 'view',
                label: gettext('Search'),
                template: 'scripts/superdesk-packaging/views/search.html',
                order: 4,
                side: 'left',
                extended: true,
                display: {authoring: false, packages: true}
            });
    }])
    .controller('SearchWidgetCtrl', SearchWidgetCtrl);

    return app;
})();
