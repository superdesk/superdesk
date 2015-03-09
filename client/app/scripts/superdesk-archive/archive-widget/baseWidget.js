(function() {
    'use strict';

    angular.module('superdesk.widgets.base', ['superdesk.itemList'])
        .factory('BaseWidgetController', function BaseWidgetControllerFactory() {
            return function BaseWidgetController($scope) {
                $scope.options = $scope.options || {};
                $scope.itemListOptions = $scope.itemListOptions || {};
                $scope.actions = $scope.actions || {};
                $scope.$watch('widget.configuration', function(config) {
                    if (config) {
                        $scope.itemListOptions.savedSearch = config.savedSearch;
                        $scope.itemListOptions.pageSize = config.maxItems;
                    }
                }, true);
                if ($scope.item) {
                    $scope.options.item = $scope.item;
                }
            };
        });
})();
