(function() {
    'use strict';

    return angular.module('superdesk.archive.directives', [
        'superdesk.filters',
        'superdesk.authoring',
        'superdesk.ingest',
        'superdesk.workflow'
    ])
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
                templateUrl: 'scripts/superdesk-archive/views/inline-meta.html',
                scope: {
                    'placeholder': '@',
                    'showmeta': '=',
                    'item': '=',
                    'setmeta': '&'
                }
            };
        })
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
        .directive('sdItemPreviewContainer', function() {
            return {
                template: '<div ng-if="item" sd-media-view data-item="item" data-close="close()"></div>',
                scope: {},
                link: function(scope) {
                    scope.item = null;

                    scope.$on('intent:preview:item', function(event, intent) {
                        scope.item = intent.data;
                    });

                    /**
                     * Close lightbox
                     */
                    scope.close = function() {
                        scope.item = null;
                    };
                }
            };
        })
        .directive('sdMediaView', ['keyboardManager', 'packages', function(keyboardManager, packages) {
            return {
                templateUrl: 'scripts/superdesk-archive/views/media-view.html',
                scope: {
                    items: '=',
                    item: '=',
                    close: '&'
                },
                link: function(scope, elem) {

                    var packageStack = [];

                    scope.singleItem = null;
                    scope.packageItem = null;

                    scope.prevEnabled = true;
                    scope.nextEnabled = true;

                    var getIndex = function(item) {
                        return _.findIndex(scope.items, {_id: item._id});
                    };

                    var setItem = function(item) {
                        resetStack();
                        scope.item = item;
                        scope.openItem(item);
                        var index = getIndex(scope.item);
                        scope.prevEnabled = index > -1 && !!scope.items[index - 1];
                        scope.nextEnabled = index > -1 && !!scope.items[index + 1];
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

                    scope.setPackageSingle = function(packageItem) {
                        packages.fetchItem(packageItem).then(function(item) {
                            scope.openItem(item);
                        });
                    };

                    scope.openItem = function(item) {
                        if (item.type === 'composite') {
                            packageStack.push(item);
                            pickPackageItem();
                        }
                        scope.setSingleItem(item);
                    };

                    scope.setSingleItem = function(item) {
                        scope.singleItem = item;
                    };

                    scope.nested = function() {
                        return packageStack.length > 1;
                    };

                    scope.previousPackage = function() {
                        _.remove(packageStack, _.last(packageStack));
                        pickPackageItem();
                        scope.setSingleItem(scope.packageItem);
                    };

                    var pickPackageItem = function() {
                        scope.packageItem = _.last(packageStack) || null;
                    };

                    var resetStack = function() {
                        packageStack = [];
                        scope.packageItem = null;
                    };

                    setItem(scope.item);
                }
            };
        }])
        .directive('sdMediaMetadata', ['userList', 'archiveService', function(userList, archiveService) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/metadata-view.html',
                link: function(scope, elem) {

                    scope.$watch('item', reloadData);

                    function reloadData() {
                        scope.originalCreator = scope.item.original_creator;
                        scope.versionCreator = scope.item.version_creator;

                        if (!archiveService.isLegal(scope.item)) {
                            if (scope.item.original_creator) {
                                userList.getUser(scope.item.original_creator)
                                    .then(function(user) {
                                        scope.originalCreator = user.display_name;
                                    });
                            }
                            if (scope.item.version_creator) {
                                userList.getUser(scope.item.version_creator)
                                    .then(function(user) {
                                        scope.versionCreator = user.display_name;
                                    });
                            }
                        }
                    }
                }
            };
        }])
        .directive('sdMediaRelated', ['familyService', 'superdesk', function(familyService, superdesk) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/related-view.html',
                link: function(scope, elem) {
                    scope.$on('item:duplicate', fetchRelatedItems);

                    scope.$watch('item', function(newVal, oldVal) {
                        if (newVal !== oldVal) {
                            fetchRelatedItems();
                        }
                    });
                    scope.open = function(item) {
                        superdesk.intent('view', 'item', item).then(null, function() {
                            superdesk.intent('edit', 'item', item);
                        });
                    };

                    function fetchRelatedItems() {
                        familyService.fetchItems(scope.item.family_id || scope.item._id, scope.item)
                        .then(function(items) {
                            scope.relatedItems = items;
                        });
                    }

                    fetchRelatedItems();
                }
            };
        }])
        .directive('sdFetchedDesks', ['desks', 'familyService', '$location', function(desks, familyService, $location) {
            return {
                scope: {
                    item: '='
                },
                templateUrl: 'scripts/superdesk-archive/views/fetched-desks.html',
                link: function(scope, elem) {
                    scope.$watchGroup(['item', 'item.archived'], function() {
                        if (scope.item) {
                            familyService.fetchDesks(scope.item, false)
                                .then(function(desks) {
                                    scope.desks = desks;
                                });
                        }
                    });

                    scope.selectFetched = function (desk) {
                        desks.setCurrentDeskId(desk.desk._id);
                        $location.path('/workspace/content').search('_id=' + desk.itemId);
                    };
                }
            };
        }])
        .directive('sdMetaIngest', ['ingestSources', function(ingestSources) {
            return {
                scope: {
                    item: '='
                },
                template: '{{name}}',
                link: function(scope) {
                    scope.$watch('item', function() {
                        scope.name = '';

                        if (!scope.item.ingest_provider && 'source' in scope.item) {
                            scope.name = scope.item.source;
                        }

                        ingestSources.initialize().then(function() {
                            if (scope.item.ingest_provider && scope.item.ingest_provider in ingestSources.providersLookup) {
                                scope.name = ingestSources.providersLookup[scope.item.ingest_provider].name;
                            }
                        });
                    });
                }
            };
        }])
        .directive('sdSingleItem', [ function() {

            return {
                templateUrl: 'scripts/superdesk-archive/views/single-item-preview.html',
                scope: {
                    item: '=',
                    contents: '=',
                    setitem: '&'
                }
            };
        }])
        .directive('sdMediaBox', ['$location', 'lock', 'multi', 'archiveService', function($location, lock, multi, archiveService) {
            return {
                restrict: 'A',
                templateUrl: 'scripts/superdesk-archive/views/media-box.html',
                link: function(scope, element, attrs) {
                    scope.lock = {isLocked: false};

                    scope.$watch('view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = 'scripts/superdesk-archive/views/media-box-list.html';
                            break;
                        default:
                            scope.itemTemplate = 'scripts/superdesk-archive/views/media-box-grid.html';
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
                            $location.search('fetch', null);
                            return scope.preview(item);
                        }
                        return false;
                    };

                    scope.toggleSelected = function(item) {
                        multi.toggle(item);
                    };

                    /**
                     * Get actions type based on item state. Used with activity filter.
                     *
                     * @param {Object} item
                     * @returns {string}
                     */
                    scope.getType = function(item) {
                        return archiveService.getType(item);
                    };
                }
            };
        }])
        .directive('sdItemCrops', ['metadata', function(metadata) {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-crops.html',
                scope: {
                    item: '='
                },
                link: function(scope, elem) {
                    metadata.initialize().then(function() {
                        scope.crop_sizes = metadata.values.crop_sizes;
                    });
                }
            };
        }])
        .directive('sdItemRendition', function() {
            return {
                templateUrl: 'scripts/superdesk-archive/views/item-rendition.html',
                scope: {
                    item: '=',
                    rendition: '@',
                    ratio: '=?'
                },
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
                                _calcRatio();
                            };

                            img.onerror = function() {
                                figure.html('');
                            };
                            img.src = href;
                        }
                    });

                    var stopRatioWatch = scope.$watch('ratio', function(val) {
                        if (val === undefined) {
                            stopRatioWatch();
                        }
                        calcRatio();
                    });

                    var calcRatio = _.debounce(_calcRatio, 150);

                    function _calcRatio() {
                        var el = elem.find('figure');
                        if (el && scope.ratio) {
                            var img = el.find('img')[0];
                            var ratio = img ? img.naturalWidth / img.naturalHeight : 1;
                            if (scope.ratio > ratio) {
                                el.parent().addClass('portrait');
                            } else {
                                el.parent().removeClass('portrait');
                            }
                        }
                    }
                }
            };
        })
        .directive('sdRatioCalc', ['$window', function($window) {
            return {
                link: function(scope, elem) {

                    var win = angular.element($window);

                    calcRatio();

                    function calcRatio() {
                        scope.ratio = elem.outerWidth() / elem.outerHeight();
                    }

                    function ratioOnResize() {
                        calcRatio();
                        scope.$apply();
                    }

                    win.bind('resize', ratioOnResize);

                    scope.$on('$destroy', function() {
                        win.unbind('resize', ratioOnResize);
                    });
                }
            };
        }])
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
                templateUrl: 'scripts/superdesk-archive/views/provider-menu.html',
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

        /*
         * This directive is only temporarly,
         * it will be deleted with content and ingest
         */
        .directive('sdContentResults', ['$location', 'preferencesService', 'packages', 'tags', 'asset',
            function ($location, preferencesService, packages, tags, asset) {
                var update = {
                    'archive:view': {
                        'allowed': [
                            'mgrid',
                            'compact'
                        ],
                        'category': 'archive',
                        'view': 'mgrid',
                        'default': 'mgrid',
                        'label': 'Users archive view format',
                        'type': 'string'
                    }
                };

                return {
                    require: '^sdSearchContainer',
                    templateUrl: asset.templateUrl('superdesk-search/views/search-results.html'),
                    link: function (scope, elem, attr, controller) {

                        var GRID_VIEW = 'mgrid',
                            LIST_VIEW = 'compact';

                        var multiSelectable = (attr.multiSelectable === undefined) ? false : true;

                        scope.flags = controller.flags;
                        scope.selected = scope.selected || {};

                        scope.preview = function preview(item) {
                            if (multiSelectable) {
                                if (_.findIndex(scope.selectedList, {_id: item._id}) === -1) {
                                    scope.selectedList.push(item);
                                } else {
                                    _.remove(scope.selectedList, {_id: item._id});
                                }
                            }
                            scope.selected.preview = item;
                            $location.search('_id', item ? item._id : null);
                        };

                        scope.openLightbox = function openLightbox() {
                            scope.selected.view = scope.selected.preview;
                        };

                        scope.closeLightbox = function closeLightbox() {
                            scope.selected.view = null;
                        };

                        scope.openSingleItem = function (packageItem) {
                            packages.fetchItem(packageItem).then(function (item) {
                                scope.selected.view = item;
                            });
                        };

                        scope.setview = setView;

                        var savedView;
                        preferencesService.get('archive:view').then(function (result) {
                            savedView = result.view;
                            scope.view = (!!savedView && savedView !== 'undefined') ? savedView : 'mgrid';
                        });

                        scope.$on('key:v', toggleView);

                        function setView(view) {
                            scope.view = view || 'mgrid';
                            update['archive:view'].view = view || 'mgrid';
                            preferencesService.update(update, 'archive:view');
                        }

                        function toggleView() {
                            var nextView = scope.view === LIST_VIEW ? GRID_VIEW : LIST_VIEW;
                            return setView(nextView);
                        }

                        /**
                         * Generates Identifier to be used by track by expression.
                         */
                        scope.generateTrackIdentifier = function(item) {
                            return (item.state === 'ingested') ? item._id : item._id + ':' + (item._current_version || item.item_version);
                        };
                    }
                };
            }])

        .service('familyService', ['api', 'desks', function(api, desks) {
            this.fetchItems = function(familyId, excludeItem) {
                var repo = 'archive';

                if (excludeItem && excludeItem._type === 'published') {
                    repo = 'published';
                }

                var filter = [
                    {not: {term: {state: 'spiked'}}},
                    {term: {family_id: familyId}}
                ];

                if (excludeItem && excludeItem._type !== 'published') {
                    filter.push({not: {term: {_id: excludeItem._id}}});
                }

                return api(repo).query({
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
                return this.fetchItems(item.state === 'ingested' ? item._id : item.family_id, excludeSelf ? item : undefined)
                .then(function(items) {
                    var deskList = [];
                    var deskIdList = [];
                    _.each(items._items, function(i) {
                        if (i.task && i.task.desk && desks.deskLookup[i.task.desk]) {
                            if (deskIdList.indexOf(i.task.desk) < 0) {
                                deskList.push({'desk': desks.deskLookup[i.task.desk], 'count': 1, 'itemId': i._id});
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
})();
