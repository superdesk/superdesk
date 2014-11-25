define([
    'lodash',
    'angular',
    'require'
], function(_, angular, require) {
    'use strict';

    return angular.module('superdesk.archive.directives', ['superdesk.authoring'])
        .directive('sdItemLock', ['api', 'lock', function(api, lock) {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-lock.html',
                scope: {item: '='},
                link: function(scope) {
                    scope.$watch('item.lock_user', function() {
                        scope.lock = null;
                        scope.lockbyme = null;
                        if (scope.item && lock.isLocked(scope.item)) {
                            api('users').getById(scope.item.lock_user).then(function(user) {
                                scope.lock = {user: user};
                            });
                        }
                        if (scope.item && lock.isLockedByMe(scope.item))
                        {
                            scope.lock = null;
                            scope.lockbyme = true;
                        }
                    });

                    scope.unlock = function() {
                        lock.unlock(scope.item).then(function() {
                            scope.item.lock_user = null;
                            scope.item.lock_sesssion = null;
                            scope.lock = null;
                            scope.isLocked = false;
                        });
                    };

                    scope.$on('item:lock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.item.lock_user = data.user;
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
                var tree = {_items: []};
                _.each(item.refs, function(ref) {
                    if (ref.idRef) {
                        tree[ref.idRef] = solveRefs(_.find(groups, {id: ref.idRef}), groups);
                    } else if (ref.residRef) {
                        tree._items.push(ref);
                    }
                });
                return tree;
            };

            return {
                replace: true,
                templateUrl: require.toUrl('./views/package.html'),
                scope: {
                    item: '=',
                    setitem: '&'
                },
                link: function(scope, elem) {
                    scope.$watch('item', function() {
                        if (scope.item !== null) {
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
                    setitem: '&'
                },
                link: function(scope, elem) {
                }
            };
        }])
        .directive('sdPackageItemProxy', ['$compile', function($compile) {
            var template = '<div sd-package-item data-id="id" data-item="item" data-setitem="setitem({selected: selected})"></div>';

            return {
                replace: true,
                scope: {
                    id: '=',
                    item: '=',
                    setitem: '&'
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
                    setitem: '&'
                },
                link: function(scope, elem) {
                    scope.data = null;
                    scope.error = null;
                    scope.type = scope.item.itemClass.split(':')[1];
                    if (scope.type !== 'text' && scope.type !== 'composite' && $rootScope.currentModule) {
                        api[$rootScope.currentModule].getById(scope.item.residRef)
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
        .directive('sdMetaIngest', ['ingestSources', function(ingestSources) {
            var promise = ingestSources.initialize();
            return {
                scope: {
                    provider: '='
                },
                template: '{{name}}',
                link: function(scope) {
                    promise.then(function() {
                        if (scope.provider) {
                            scope.name = ingestSources.providersLookup[scope.provider].name;
                        }
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
                        scope.isLocked = item && (lock.isLocked(item) || lock.isLockedByMe(item));
                    });

                    scope.$on('item:lock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.isLocked = true;
                            scope.item.lock_user = data.user;
                            scope.$digest();
                        }
                    });

                    scope.$on('item:unlock', function(_e, data) {
                        if (scope.item && scope.item._id === data.item) {
                            scope.isLocked = false;
                            scope.item.lock_user = null;
                            scope.item.lock_session = null;
                            scope.$digest();
                        }
                    });
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
        });
});
