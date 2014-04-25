define(['lodash', 'require'], function(_, require) {
    'use strict';

    return ['keyboardManager', function(keyboardManager) {
        return {
            replace: true,
            templateUrl: require.toUrl('./views/media-view.html'),
            scope: {
                items: '=',
                item: '='
            },
            link: function(scope, elem) {
                scope.prevEnabled = true;
                scope.nextEnabled = true;

                var getIndex = function(item) {
                    return _.findIndex(scope.items.collection, item);
                };

                var setItem = function(item) {
                    scope.item = item;
                    var index = getIndex(scope.item);
                    scope.prevEnabled = !!scope.items.collection[index - 1];
                    scope.nextEnabled = !!scope.items.collection[index + 1];
                };

                scope.prev = function() {
                    var index = getIndex(scope.item);
                    if (index > 0) {
                        setItem(scope.items.collection[index - 1]);
                    }
                };
                scope.next = function() {
                    var index = getIndex(scope.item);
                    if (index !== -1 && index < scope.items.collection.length - 1) {
                        setItem(scope.items.collection[index + 1]);
                    }
                };

                keyboardManager.push('left', scope.prev);
                keyboardManager.push('right', scope.next);
                scope.$on('$destroy', function() {
                    keyboardManager.pop('left');
                    keyboardManager.pop('right');
                });

                setItem(scope.item);
            }
        };
    }];
});
