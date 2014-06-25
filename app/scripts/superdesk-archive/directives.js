define([
    'lodash',
    'angular',
    'require'
], function(_, angular, require) {
    'use strict';

    return angular.module('superdesk.archive.directives', [])
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
                scope: {item: '='},
                link: function(scope, elem) {
                    scope.$watch('item', function() {
                        scope.tree = solveRefs(
                            _.find(scope.item.groups, {id: 'root'}),
                            scope.item.groups
                        );
                    });
                }
            };
        }])
        .directive('sdPackageItem', [function() {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/package-item.html'),
                scope: {id: '=', item: '='},
                link: function(scope, elem) {

                }
            };
        }])
        .directive('sdPackageItemProxy', ['$compile', function($compile) {
            var template = '<div sd-package-item data-id="id" data-item="item"></div>';

            return {
                replace: true,
                scope: {id: '=', item: '='},
                link: function(scope, elem) {
                    elem.append($compile(template)(scope));
                }
            };
        }])
        .directive('sdPackageRef', ['api', function(api) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/package-ref.html'),
                scope: {item: '='},
                link: function(scope, elem) {
                    scope.data = null;
                    api.ingest.getById(scope.item.residRef)
                    .then(function(result) {
                        scope.data = result;
                    });
                }
            };
        }])
        .directive('sdMediaPreview', ['api', function(api) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/preview.html'),
                scope: {item: '='}
            };
        }])
        .directive('sdMediaView', ['keyboardManager', 'api', function(keyboardManager, api) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/media-view.html'),
                scope: {
                    items: '=',
                    item: '='
                },
                link: function(scope, elem) {

                    scope.singleItem = null;
                    scope.packageContents = null;

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

                    scope.setSingleItem = function(item) {
                        scope.singleItem = item;
                        if (scope.singleItem !== null) {
                            if (scope.singleItem.type === 'composite') {
                                scope.packageContents = [];

                                var mainPackage = _.find(scope.singleItem.groups, {id: 'main'});

                                _.each(mainPackage.refs, function(r) {

                                    api.ingest.getById(r.residRef)
                                        .then(function(item) {
                                            scope.packageContents.push(item);
                                        }, function(response) {
                                            if (response.status === 404) {
                                                console.log('Item not found');
                                            }
                                        });
                                });
                            }
                        }
                    };

                    setItem(scope.item);
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
                },
                link: function(scope, elem) {

                }
            };
        }])
        .directive('sdSidebarLayout', ['$location', '$filter', function($location, $filter) {
            return {
                transclude: true,
                templateUrl: require.toUrl('./views/sidebar.html')
            };
        }])
        .directive('sdMediaBox', function() {
            return {
                restrict: 'A',
                templateUrl: require.toUrl('./views/media-box.html'),
                link: function(scope, element, attrs) {
                    if (!scope.activityFilter && scope.extras) {
                        scope.activityFilter = scope.extras.activityFilter;
                    }
                    scope.$watch('extras.view', function(view) {
                        switch (view) {
                        case 'mlist':
                        case 'compact':
                            scope.itemTemplate = require.toUrl('./views/media-box-list.html');
                            break;
                        default:
                            scope.itemTemplate = require.toUrl('./views/media-box-grid.html');
                        }
                    });
                }
            };
        })
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
                                    figure.prepend(img);
                                }
                            };

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
        .directive('sdToggleBox', function() {
            return {
                templateUrl: require.toUrl('./views/toggleBox.html'),
                replace: true,
                transclude: true,
                scope: true,
                link: function($scope, element, attrs) {
                    $scope.title = attrs.title;
                    $scope.isOpen = attrs.open === 'true';
                    $scope.icon = attrs.icon;
                    $scope.toggleModule = function() {
                        $scope.isOpen = !$scope.isOpen;
                    };
                }
            };
        })
        .directive('sdFilterUrgency', ['$location', function($location) {
            return {
                scope: true,
                link: function($scope, element, attrs) {

                    $scope.urgency = {
                        min: $location.search().urgency_min || 1,
                        max: $location.search().urgency_max || 5
                    };

                    function handleUrgency(urgency) {
                        var min = Math.round(urgency.min);
                        var max = Math.round(urgency.max);
                        if (min !== 1 || max !== 5) {
                            var urgency_norm = {
                                min: min,
                                max: max
                            };
                            $location.search('urgency_min', urgency_norm.min);
                            $location.search('urgency_max', urgency_norm.max);
                        } else {
                            $location.search('urgency_min', null);
                            $location.search('urgency_max', null);
                        }
                    }

                    var handleUrgencyWrap = _.throttle(handleUrgency, 2000);

                    $scope.$watchCollection('urgency', function(newVal) {
                        handleUrgencyWrap(newVal);
                    });
                }
            };
        }])
        .directive('sdFilterContenttype', [ '$location', function($location) {
            return {
                restrict: 'A',
                templateUrl: require.toUrl('./views/filter-contenttype.html'),
                replace: true,
                scope: {
                    items: '='
                },
                link: function(scope, element, attrs) {

                    scope.contenttype = [
                        {
                            term: 'text',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'audio',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'video',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'picture',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'graphic',
                            checked: false,
                            count: 0
                        },
                        {
                            term: 'composite',
                            checked: false,
                            count: 0
                        }
                    ];

                    var search = $location.search();
                    if (search.type) {
                        var type = JSON.parse(search.type);
                        _.forEach(type, function(term) {
                            _.extend(_.first(_.where(scope.contenttype, {term: term})), {checked: true});
                        });
                    }

                    scope.$watchCollection('items', function() {
                        if (scope.items && scope.items._facets !== undefined) {
                            _.forEach(scope.items._facets.type.terms, function(type) {
                                _.extend(_.first(_.where(scope.contenttype, {term: type.term})), type);
                            });
                        }
                    });

                    scope.setContenttypeFilter = function() {
                        var contenttype = _.map(_.where(scope.contenttype, {'checked': true}), function(t) {
                            return t.term;
                        });
                        if (contenttype.length === 0) {
                            $location.search('type', null);
                        } else {
                            $location.search('type', JSON.stringify(contenttype));
                        }
                    };
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
