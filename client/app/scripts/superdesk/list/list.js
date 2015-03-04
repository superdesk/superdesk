define([
    'angular',
    'require',
    './list-view-directive',
    './searchbar-directive',
    './list-item-directive'
], function(angular, require) {
    'use strict';

    var mod = angular.module('superdesk.list', []);
    mod.directive('sdListView', require('./list-view-directive'));
    mod.directive('sdSearchbar', require('./searchbar-directive'));
    mod.directive('sdListItem', require('./list-item-directive'));

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
            templateUrl: require.toUrl('./views/sdPagination.html'),
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
                        window.scrollTo(0, 0);
                    }
                });

                /**
                 * Set page
                 *
                 * @param {integer} page
                 */
                scope.setPage = function(page) {
                    $location.search('page', page > 1 ? page : null);
                };
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

    // Alternative sdPagination, doesn't use $location.
    // Should replace sdPagination.
    mod.directive('sdPaginationAlt', [function() {
        return {
            templateUrl: require.toUrl('./views/sdPaginationAlt.html'),
            scope: {
                page: '=',
                maxPage: '='
            },
            link: function(scope, element, attrs) {
            }
        };
    }]);

    return mod;
});
