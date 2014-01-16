define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    angular.module('superdesk')
        .directive('sdListView', function($route, $location) {
            return {
                scope: {
                    select: '&',
                    adapter: '=',
                    itemTemplate: '@'
                },
                templateUrl: 'scripts/superdesk/views/list-view.html',
                transclude: true,
                link: function(scope, elem, attrs) {

                    scope.clickItem = function(item) {
                        scope.selected = item;
                        scope.select({item: item});
                        $location.search('_id', item._id);
                    };

                    scope.$watch('adapter._items', function(items) {
                        scope.items = items;
                        if (items && $route.current.params._id) {
                            var match = _.find(items, {_id: $route.current.params._id});
                            if (match) {
                                scope.clickItem(match);
                            } else if (!scope.selected || $route.current.params._id !== scope.selected._id) {
                                scope.adapter.find($route.current.params._id).then(function(item) {
                                    scope.clickItem(item);
                                });
                            }
                        }
                    });
                }
            };
        });
});