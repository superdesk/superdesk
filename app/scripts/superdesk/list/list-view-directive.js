define(['require', 'lodash'], function(require, _) {
    'use strict';

    return ['$location', 'keyboardManager', function($location, keyboardManager) {
        return {
            scope: {
                select: '&',
                extras: '=',
                items: '='
            },
            replace: true,
            transclude: true,
            templateUrl: require.toUrl('./views/list-view.html'),
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
                    }/* else if (!scope.selected || itemId !== scope.selected._id) {
                        scope.adapter.find(itemId).then(function(item) {
                            scope.clickItem(item);
                        });
                    }*/
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

                scope.clickItem = function(item) {
                    scope.selected = item;
                    scope.select({item: item});
                };

                scope.$watch('items', function() {
                    fetchSelectedItem($location.search()._id);
                    elem.find('.list-view').focus();
                });
            }
        };
    }];
});
