define(['angular', 'lodash'], function(angular, _) {
    'use strict';

    angular.module('superdesk')
        .directive('sdListView', ['$location', function($location) {
            return {
                scope: {
                    select: '&',
                    extras: '=',
                    adapter: '=',
                    itemTemplate: '@'
                },
                transclude: true,
                replace: true,
                templateUrl: 'scripts/superdesk/views/list-view.html',
                link: function(scope, elem, attrs) {

                    scope.clickItem = function(item) {
                        scope.selected = item;
                        scope.select({item: item});
                        $location.search('_id', item._id);
                    };

                    function fetchSelectedItem(itemId, items) {
                        if (itemId) {
                            var match = _.find(items, {_id: itemId});
                            if (match) {
                                scope.clickItem(match);
                            } else if (!scope.selected || itemId !== scope.selected._id) {
                                scope.adapter.find(itemId).then(function(item) {
                                    scope.clickItem(item);
                                });
                            }
                        }
                    }

                    scope.$watch('adapter._items', function(items) {
                        scope.items = items;
                        if (items) {
                            fetchSelectedItem($location.search()._id, items);
                        }
                    });
                }
            };
        }]);
});