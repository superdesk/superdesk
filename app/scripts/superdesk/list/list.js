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

    mod.directive('sdUpdown', ['$location', 'keyboardManager', function($location, keyboardManager) {
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
                items: '=',
                limit: '='
            },
            link: function(scope, element, attrs) {

                scope.$watch('items._meta', function(meta) {
                    scope.total = 0;
                    if (meta) {
                        scope.total = meta.total;
                        scope.page = $location.search().page || 1;
                        scope.lastPage = scope.limit ? Math.ceil(scope.total / scope.limit) : scope.page;
                        scope.from = (scope.page - 1) * scope.limit + 1;
                        scope.to = Math.min(scope.total, scope.from + scope.limit - 1);
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
            }
        };
    }]);

    return mod;
});
