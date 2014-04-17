define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    return angular.module('superdesk.list', [])
        .directive('sdListView', ['$location', 'keyboardManager', function($location, keyboardManager) {
            return {
                scope: {
                    select: '&',
                    extras: '=',
                    adapter: '='
                },
                replace: true,
                transclude: true,
                templateUrl: 'scripts/superdesk/views/list-view.html',
                link: function(scope, elem, attrs) {
                    var MOVE_UP = -1,
                        MOVE_DOWN = 1;

                    function fetchSelectedItem(itemId) {
                        if (!itemId) {
                            return;
                        }

                        var match = _.find(scope.items, {_id: itemId});
                        if (match) {
                            scope.clickItem(match);
                        } else if (!scope.selected || itemId !== scope.selected._id) {
                            scope.adapter.find(itemId).then(function(item) {
                                scope.clickItem(item);
                            });
                        }
                    }

                    function selectItem(diff) {
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
                    }

                    function onKey(dir, callback) {
                        keyboardManager.bind(dir, callback);
                    }

                    onKey('up', function() {
                        selectItem(MOVE_UP);
                    });

                    onKey('down', function() {
                        selectItem(MOVE_DOWN);
                    });

                    scope.clickItem = function(item) {
                        scope.selected = item;
                        scope.select({item: item});
                        $location.search('_id', item ? item._id : null);
                    };

                    scope.$watch('adapter.collection', function(items) {
                        scope.items = items;
                        fetchSelectedItem($location.search()._id);
                        elem.find('.list-view').focus();
                    });
                }
            };
        }]);
});
