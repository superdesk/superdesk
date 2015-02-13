define([
    'lodash',
    'angular',
    'require'
], function(_, angular, require) {
    'use strict';

    return angular.module('superdesk.archive.directives', ['superdesk.authoring'])
        .directive('sdItemLock', ['api', 'lock', 'privileges', function(api, lock, privileges) {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-lock.html',
                scope: {item: '='},
                link: function(scope) {

                    init();

                    scope.$watch('item.lock_session', function() {
                        init();

                        if (scope.item && lock.isLocked(scope.item)) {
                            api('users').getById(scope.item.lock_user).then(function(user) {
                                scope.lock.user = user;
                                scope.lock.lockbyme = lock.isLockedByMe(scope.item);
                            });
                        }
                    });

                    function init() {
                        scope.privileges = privileges.privileges;
                        scope.lock = {user: null, lockbyme: false};
                    }

                    scope.unlock = function() {
                        lock.unlock(scope.item).then(function() {
                            scope.item.lock_user = null;
                            scope.item.lock_session = null;
                            scope.lock = null;
                            scope.isLocked = false;
                        });
                    };

                    scope.can_unlock = function() {
                        return lock.can_unlock(scope.item);
                    };

                    scope.$on('item:lock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.item.lock_user = data.user;
                            scope.item.lock_time = data.lock_time;
                            scope.item.lock_session = data.lock_session;
                            scope.$digest();
                        }
                    });

                    scope.$on('item:unlock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.item.lock_user = null;
                            scope.item.lock_session = null;
                            scope.$digest();
                        }
                    });
                }
            };
        }])
        .directive('sdInlineMeta', function() {
            return {
                templateUrl: require.toUrl('./views/inline-meta.html'),
                scope: {
                    'placeholder': '@',
                    'showmeta': '=',
                    'item': '=',
                    'setmeta': '&'
                }
            };
        })
        .directive('sdPackage', [function() {
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
                replace: true,
                templateUrl: require.toUrl('./views/package.html'),
                scope: {
                    item: '=',
                    setitem: '&',
                    remove: '&',
                    editmode: '='
                },
                link: function(scope, elem) {
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
        }])
        .directive('sdPackageItem', [function() {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/package-item.html'),
                scope: {
                    id: '=',
                    item: '=',
                    setitem: '&',
                    remove: '&',
                    editmode: '='
                },
                link: function(scope, elem) {
                }
            };
        }])
        .directive('sdPackageItemProxy', ['$compile', function($compile) {
            var template =
                '<div sd-package-item data-id="id"' +
                    ' data-item="item"' +
                    ' data-setitem="setitem({selected: selected})"' +
                    ' data-remove="remove({item: item})"' +
                    ' data-editmode="editmode">' +
                '</div>';

            return {
                replace: true,
                scope: {
                    id: '=',
                    item: '=',
                    setitem: '&',
                    remove: '&',
                    editmode: '='
                },
                link: function(scope, elem) {
                    elem.append($compile(template)(scope));
                }
            };
        }])
        .directive('sdPackageRef', ['api', '$rootScope', function(api, $rootScope) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/package-ref.html'),
                scope: {
                    item: '=',
                    setitem: '&',
                    remove: '&',
                    editmode: '='
                },
                link: function(scope, elem) {
                    scope.data = null;
                    scope.error = null;
                    scope.type = scope.item.type || scope.item.itemClass.split(':')[1];
                    if (scope.type !== 'text' && scope.type !== 'composite' && scope.item.location) {
                        api[scope.item.location].getById(scope.item.residRef)
                        .then(function(result) {
                            scope.data = result;
                        }, function(response) {
                            scope.error = true;
                        });
                    }
                }
            };
        }])
        .directive('sdMediaPreview', [function() {
            return {
                templateUrl: 'scripts/superdesk-archive/views/preview.html'
            };
        }])
        .directive('sdMediaPreviewWidget', [function() {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/archive-widget/item-preview.html'
            };
        }])
        .directive('sdMediaView', ['keyboardManager', 'api', function(keyboardManager, api) {
            return {
                templateUrl: 'scripts/superdesk-archive/views/media-view.html',
                scope: {
                    items: '=',
                    item: '=',
                    close: '&'
                },
                link: function(scope, elem) {

                    scope.singleItem = null;

                    scope.prevEnabled = true;
                    scope.nextEnabled = true;

                    var getIndex = function(item) {
                        return _.findIndex(scope.items, item);
                    };

                    var setItem = function(item) {
                        scope.item = item;
                        scope.setSingleItem(item);
                        var index = getIndex(scope.item);
                        scope.prevEnabled = !!scope.items[index - 1];
                        scope.nextEnabled = !!scope.items[index + 1];
                    };

                    scope.prev = function() {
                        var index = getIndex(scope.item);
                        if (index > 0) {
                            setItem(scope.items[index - 1]);
                        }
                    };
                    scope.next = function() {
                        var index = getIndex(scope.item);
                        if (index !== -1 && index < scope.items.length - 1) {
                            setItem(scope.items[index + 1]);
                        }
                    };

                    keyboardManager.push('left', scope.prev);
                    keyboardManager.push('right', scope.next);
                    scope.$on('$destroy', function() {
                        keyboardManager.pop('left');
                        keyboardManager.pop('right');
                    });

                    scope.setPackageSingle = function(selected) {
                        api.ingest.getById(selected)
                            .then(function(item) {
                                scope.setSingleItem(item);
                            }, function(response) {
                                if (response.status === 404) {
                                    console.log('Item not found');
                                }
                            });

                    };

                    scope.setSingleItem = function(item) {
                        scope.singleItem = item;
                    };

                    setItem(scope.item);
                }
            };
        }])
        .directive('sdMediaMetadata', ['userList', function(userList) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/metadata-view.html',
                link: function(scope, elem) {

                    scope.$watch('item', reloadData);

                    function reloadData() {
                        scope.original_creator = null;
                        scope.version_creator = null;

                        if (scope.item.original_creator) {
                            userList.getUser(scope.item.original_creator).then(function(user) {
                                scope.original_creator = user.display_name;
                            });
                        }
                        if (scope.item.version_creator) {
                            userList.getUser(scope.item.version_creator).then(function(user) {
                                scope.version_creator = user.display_name;
                            });
                        }
                    }
                }
            };
        }])
        .directive('sdMediaRelated', ['familyService', function(familyService) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/related-view.html',
                link: function(scope, elem) {
                    scope.$watch('item', function() {
                        familyService.fetchItems(scope.item.family_id || scope.item._id, scope.item)
                        .then(function(items) {
                            scope.relatedItems = items;
                        });
                    });
                }
            };
        }])
        .directive('sdFetchedDesks', ['familyService', function(familyService) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/fetched-desks.html',
                link: function(scope, elem) {
                    scope.$watch('item', function() {
                        familyService.fetchDesks(scope.item, false)
                        .then(function(desks) {
                            scope.desks = desks;
                        });
                    });
                }
            };
        }])
        .directive('sdMetaIngest', ['ingestSources', function(ingestSources) {
            var promise = ingestSources.initialize();
            return {
                scope: {
                    provider: '='
                },
                template: '{{name}}',
                link: function(scope) {
                    scope.$watch('provider', function() {
                        scope.name = '';
                        promise.then(function() {
                            if (scope.provider && scope.provider in ingestSources.providersLookup) {
                                scope.name = ingestSources.providersLookup[scope.provider].name;
                            }
                        });
                    });
                }
            };
        }])
        .directive('sdSingleItem', [ function() {

            return {
                replace: true,
                templateUrl: require.toUrl('./views/single-item-preview.html'),
                scope: {
                    item: '=',
                    contents: '='
                }
            };
        }])
        .directive('sdMediaBox', ['lock', function(lock) {
            return {
                restrict: 'A',
                templateUrl: require.toUrl('./views/media-box.html'),
                link: function(scope, element, attrs) {
                    scope.lock = {isLocked: false};

                    scope.$watch('view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = require.toUrl('./views/media-box-list.html');
                            break;
                        default:
                            scope.itemTemplate = require.toUrl('./views/media-box-grid.html');
                        }
                    });

                    scope.$watch('item', function(item) {
                        scope.lock.isLocked = item && (lock.isLocked(item) || lock.isLockedByMe(item));
                    });

                    scope.$on('item:lock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.lock.isLocked = true;
                            scope.item.lock_user = data.user;
                            scope.item.lock_session = data.lock_session;
                            scope.item.lock_time = data.lock_time;
                            scope.$digest();
                        }
                    });

                    scope.$on('item:unlock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.lock.isLocked = false;
                            scope.item.lock_user = null;
                            scope.item.lock_session = null;
                            scope.item.lock_time = null;
                            scope.$digest();
                        }
                    });

                    scope.$on('task:progress', function(_e, data) {
                        if (data.task === scope.item.task_id) {
                            if (data.progress.total === 0) {
                                scope._progress = 10;
                            } else {
                                scope._progress = Math.min(100, Math.round(100.0 * data.progress.current / data.progress.total));
                            }
                            scope.$digest();
                        }
                    });

                    scope.clickAction =  function clickAction(item) {
                        if (typeof scope.preview === 'function') {
                            return scope.preview(item);
                        }
                        return false;
                    };
                }
            };
        }])
        .directive('sdItemRendition', function() {
            return {
                templateUrl: require.toUrl('./views/item-rendition.html'),
                scope: {item: '=', rendition: '@'},
                link: function(scope, elem) {
                    scope.$watch('item.renditions[rendition].href', function(href) {
                        var figure = elem.find('figure'),
                            oldImg = figure.find('img').css('opacity', 0.5);
                        if (href) {
                            var img = new Image();
                            img.onload = function() {
                                if (oldImg.length) {
                                    oldImg.replaceWith(img);
                                } else {
                                    figure.html(img);
                                }
                            };

                            img.onerror = function() {};
                            img.src = href;
                        }
                    });
                }
            };
        })
        .directive('sdHtmlPreview', ['$sce', function($sce) {
            return {
                scope: {sdHtmlPreview: '='},
                template: '<div ng-bind-html="html"></div>',
                link: function(scope, elem, attrs) {
                    scope.$watch('sdHtmlPreview', function(html) {
                        scope.html = $sce.trustAsHtml(html);
                    });
                }
            };
        }])
        .directive('sdProviderMenu', ['$location', function($location) {
            return {
                scope: {items: '='},
                templateUrl: require.toUrl('./views/provider-menu.html'),
                link: function(scope, element, attrs) {

                    scope.setProvider = function(provider) {
                        scope.selected = provider;
                        $location.search('provider', scope.selected);
                    };

                    scope.$watchCollection(function() {
                        return $location.search();
                    }, function(search) {
                        if (search.provider) {
                            scope.selected = search.provider;
                        }
                    });

                }
            };
        }])

        .directive('sdGridLayout', function() {
            return {
                templateUrl: 'scripts/superdesk-items-common/views/grid-layout.html',
                scope: {items: '='},
                link: function(scope, elem, attrs) {
                    scope.view = 'mgrid';

                    scope.preview = function(item) {
                        scope.previewItem = item;
                    };
                }
            };
        })

        .service('familyService', ['api', 'desks', function(api, desks) {
            this.fetchItems = function(familyId, excludeItem) {
                var filter = [
                    {not: {term: {state: 'spiked'}}},
                    {term: {family_id: familyId}}
                ];
                if (excludeItem) {
                    filter.push({not: {term: {_id: excludeItem._id}}});
                }
                return api('archive').query({
                    source: {
                        query: {filtered: {filter: {
                            and: filter
                        }}},
                        sort: [{versioncreated: 'desc'}],
                        size: 100,
                        from: 0
                    }
                });
            };
            this.fetchDesks = function(item, excludeSelf) {
                return this.fetchItems(item.family_id || item._id, excludeSelf ? item : undefined)
                .then(function(items) {
                    var deskList = [];
                    var deskIdList = [];
                    _.each(items._items, function(i) {
                        if (i.task && i.task.desk && desks.deskLookup[i.task.desk]) {
                            if (deskIdList.indexOf(i.task.desk) < 0) {
                                deskList.push({'desk': desks.deskLookup[i.task.desk], 'count': 1});
                                deskIdList.push(i.task.desk);
                            } else {
                                deskList[deskIdList.indexOf(i.task.desk)].count += 1;
                            }
                        }
                    });
                    return deskList;
                });
            };
        }]);
});
