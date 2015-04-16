(function() {
    'use strict';

    function ListItemDirectiveFactory() {
        return {
            link: function(scope, element, attrs, controller, $transclude) {
                var itemScope;

                scope.$watch('item', function() {
                    destroyItemScope();
                    itemScope = scope.$parent.$parent.$new();
                    itemScope.item = scope.item;
                    itemScope.items = scope.items;
                    itemScope.extras = scope.extras;
                    itemScope.$index = scope.$index;
                    $transclude(itemScope, function(clone) {
                        element.empty();
                        element.append(clone);
                    });
                });

                scope.$on('$destroy', destroyItemScope);

                function destroyItemScope() {
                    if (itemScope) {
                        itemScope.$destroy();
                    }
                }
            }
        };
    }

    var mod = angular.module('superdesk.list', ['superdesk.keyboard']);
    mod.directive('sdListView', ['$location', 'keyboardManager', function($location, keyboardManager) {
        return {
            scope: {
                select: '&',
                extras: '=',
                items: '='
            },
            replace: true,
            transclude: true,
            templateUrl: 'scripts/superdesk/list/views/list-view.html',
            link: function(scope, elem, attrs) {
                var UP = -1,
                    DOWN = 1;

                function fetchSelectedItem(itemId) {
                    if (!itemId) {
                        return;
                    }

                    var match = _.find(scope.items, {_id: itemId});
                    if (match) {
                        scope.clickItem(match);
                    }
                }

                function move(diff) {
                    return function() {
                        if (scope.items) {
                            var index = _.indexOf(scope.items, scope.selected);
                            if (index === -1) { // selected not in current items, select first
                                return scope.clickItem(_.first(scope.items));
                            }

                            var nextIndex = _.max([0, _.min([scope.items.length - 1, index + diff])]);
                            if (nextIndex < 0) {
                                return scope.clickItem(_.last(scope.items));
                            }

                            return scope.clickItem(scope.items[nextIndex]);
                        }
                    };
                }

                function onKey(dir, callback) {
                    keyboardManager.bind(dir, callback);
                }

                onKey('up', move(UP));
                onKey('left', move(UP));
                onKey('down', move(DOWN));
                onKey('right', move(DOWN));

                scope.clickItem = function(item, $event) {
                    scope.selected = item;
                    scope.select({item: item});
                    if ($event) {
                        $event.stopPropagation();
                    }
                };

                scope.$watch('items', function() {
                    fetchSelectedItem($location.search()._id);
                    elem.find('.list-view').focus();
                });
            }
        };
    }]);

    mod.directive('sdSearchbar', ['$location', function($location) {
        return {
            scope: true,
            templateUrl: 'scripts/superdesk/list/views/searchbar.html',
            link: function(scope, elem) {
                var input = elem.find('#search-input');
                scope.q = $location.search().q || null;
                scope.flags = {extended: !!scope.q};

                scope.search = function() {
                    $location.search('q', scope.q || null);
                    $location.search('page', null);
                };

                scope.close = function() {
                    scope.q = null;
                    input.focus();
                };
            }
        };
    }]);

    mod.directive('sdListItem', ListItemDirectiveFactory);

    mod.directive('sdUpdown', ['$location', 'keyboardManager', '$anchorScroll', function($location, keyboardManager, $anchorScroll) {
        return {
            transclude: true,
            template: '<div ng-transclude></div>',
            scope: {
                'items': '=',
                'select': '&'
            },
            link: function(scope, elem, attrs) {
                var UP = -1,
                    DOWN = 1;

                function fetchSelectedItem(itemId) {
                    if (!itemId) {
                        return;
                    }

                    var match = _.find(scope.items, {_id: itemId});
                    if (match) {
                        clickItem(match);
                    }
                }
                function scrollList(id) {
                    $location.hash(id);
                    $anchorScroll();
                }
                function move(diff) {
                    return function() {
                        if (scope.items) {
                            var index = _.findIndex(scope.items, {_id: $location.search()._id});
                            if (index === -1) { // selected not in current items, select first
                                return clickItem(_.first(scope.items));
                            }
                            var nextIndex = _.max([0, _.min([scope.items.length - 1, index + diff])]);
                            if (nextIndex < 0) {
                                return clickItem(_.last(scope.items));
                            }
                            scrollList(scope.items[nextIndex]._id);

                            return clickItem(scope.items[nextIndex]);
                        }
                    };
                }

                function onKey(dir, callback) {
                    keyboardManager.bind(dir, callback);
                }

                onKey('up', move(UP));
                onKey('left', move(UP));
                onKey('down', move(DOWN));
                onKey('right', move(DOWN));

                function clickItem(item, $event) {
                    scope.select({item: item});
                    if ($event) {
                        $event.stopPropagation();
                    }

                }

                scope.$watch('items', function() {
                    fetchSelectedItem($location.search()._id);
                    elem.find('.list-view').focus();
                });
            }

        };
    }]);

    /**
     * sdPagination inserts pagination controls for a given data set.
     *
     * Usage:
     * <div sd-pagination data-items="users" data-limit="maxResults"></div>
     *
     * Params:
     * @items {object} Item container as received from server, with _items and _meta.
     * @limit {number} Number of items per page.
     */
    mod.directive('sdPagination', ['$location', function($location) {
        return {
            templateUrl: 'scripts/superdesk/list/views/sdPagination.html',
            scope: {
                items: '='
            },
            link: function(scope, element, attrs) {
                var size = 25;
                scope.pgsizes = [25, 50, 100];
                scope.$watch('items._meta', function(meta) {
                    scope.total = 0;
                    if (meta) {
                        scope.total = meta.total;
                        scope.page = Number($location.search().page) || 1;
                        scope.limit = Number(localStorage.getItem('pagesize')) || Number($location.search().max_results) || size;
                        scope.lastPage = scope.limit ? Math.ceil(scope.total / scope.limit) : scope.page;
                        scope.from = (scope.page - 1) * scope.limit + 1;
                        scope.to = Math.min(scope.total, scope.from + scope.limit - 1);
                        if (scope.pageChanged === true) {
                            scrollTop();
                            scope.pageChanged = null;
                        }
                    }
                });
                /**
                 * Set page
                 *
                 * @param {integer} page
                 */
                scope.setPage = function(page) {
                    $location.search('page', page > 1 ? page : null);
                    scope.pageChanged = true;
                };

                function scrollTop() {
                    window.scrollTo(0, 0);
                }
                /*
                * Set custom page size limit
                *@param {integer} page
                */
                scope.setLimit = function(pagesize) {
                    localStorage.setItem('pagesize', pagesize);
                    scope.setPage(0);
                    $location.search('max_results', pagesize != null ? pagesize : size);
                };
            }
        };
    }]);
    mod.directive('sdScrolled', ['$location', function($location) {
        return {
            scope: {
                nextAction: '=',
                previousAction: '='
            },
            link: function(scope, elm, attr) {
                var page = 1;
                if ($location.search().page) {
                    page = $location.search().page;
                }
                var container = elm[0];
                elm.bind('scroll', function() { console.log('scrolled');
                    if (container.scrollTop + container.offsetHeight >= container.scrollHeight - 250) {
                        if (scope.nextAction) {
                            scope.nextAction();
                        }
                    }
                });
            }
        };
    }]);
    // Alternative sdPagination, doesn't use $location.
    // Should replace sdPagination.
    mod.directive('sdPaginationAlt', [function() {
        return {
            templateUrl: 'scripts/superdesk/list/views/sdPaginationAlt.html',
            scope: {
                page: '=',
                maxPage: '='
            }
        };
    }]);

    return mod;
})();
