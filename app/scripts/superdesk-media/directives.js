define([
    'lodash',
    'jquery',
    'angular',
    'require'
], function(_, $, angular, require) {
    'use strict';

    angular.module('superdesk.media.directives', [])

        .directive('sdInlineMeta', function() {
            return {
                templateUrl: require.toUrl('./views/sd-inline-meta.html'),
                scope: {
                    'placeholder': '@',
                    'showmeta': '=',
                    'item': '=',
                    'setmeta': '&'
                }
            };
        })
        .directive('sdMediaPreview', [
        function() {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/preview.html'),
                scope: {
                    item: '='
                },
                link: function(scope, elem) {
                }
            };
        }])
        .directive('sdMediaView', ['keyboardManager',
        function(keyboardManager) {
            return {
                replace: true,
                templateUrl: require.toUrl('./views/view.html'),
                scope: {
                    items: '=',
                    item: '='
                },
                link: function(scope, elem) {
                    scope.prevEnabled = true;
                    scope.nextEnabled = true;

                    var getIndex = function(item) {
                        return _.findIndex(scope.items.collection, {GUID: item.GUID});
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

                    keyboardManager.bind('left', scope.prev);
                    keyboardManager.bind('right', scope.next);

                    setItem(scope.item);
                }
            };
        }]);
});
