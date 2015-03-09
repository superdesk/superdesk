(function() {
    'use strict';

    angular.module('superdesk.widgets.base', ['superdesk.itemList'])
        .factory('BaseWidgetController', ['$location', '$timeout', 'superdesk', 'search', 'preferencesService', 'notify', 'ItemList',
        function BaseWidgetControllerFactory($location, $timeout, superdesk, search, preferencesService, notify, ItemList) {

            return function BaseWidgetController($scope) {
                $scope.options = $scope.options || {};
                $scope.itemListOptions = $scope.itemListOptions || {};
                $scope.actions = $scope.actions || {};
                $scope.$watch('widget.configuration', function() {
                    if ($scope.widget.configuration) {
                        $scope.itemListOptions.search = $scope.widget.configuration.search;
                        $scope.itemListOptions.pageSize = $scope.widget.configuration.maxItems;
                        if ($scope.widget.configuration.provider === 'all') {
                            $scope.itemListOptions.provider = null;
                        } else {
                            $scope.itemListOptions.provider = $scope.widget.configuration.provider;
                        }
                    }
                }, true);
                if ($scope.item) {
                    $scope.options.item = $scope.item;
                }
            };
        }])
        .factory('BaseWidgetConfigController', [
        function BaseWidgetConfigControllerFactory() {

            return function BaseWidgetConfigController($scope) {
                $scope.fetchProviders = function() {
                    $scope.api.query({source: {size: 0}}).then(function(items) {
                        $scope.availableProviders = ['all'].concat(_.pluck(items._aggregations.source.buckets, 'key'));
                    });
                };

                $scope.notIn = function(haystack) {
                    return function(needle) {
                        return haystack.indexOf(needle) === -1;
                    };
                };
            };
        }]);
})();
