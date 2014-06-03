define([
    'angular',
    'require'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.widgets.ingest', [])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('ingest', {
                label: 'Ingest',
                multiple: true,
                icon: 'ingest',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.png'),
                template: require.toUrl('./widget-ingest.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                description: 'Ingest widget'
            });
        }])
        .controller('IngestController', ['$scope', '$timeout', 'superdesk', 'api', 'es',
        function ($scope, $timeout, superdesk, api, es) {
            var timeoutId;

            function refresh(config) {
                var params = {
                    q: config.search || undefined,
                    size: config.maxItems
                };
                var filters = [];
                if (config.provider && config.provider !== 'all') {
                    filters.push({term: {provider: config.provider}});
                }
                var criteria = es(params, filters);

                api.ingest.query({source: criteria}).then(function(items) {
                    $scope.items = items;
                    timeoutId = $timeout(function() {
                        refresh(config);
                    }, config.updateInterval * 1000 * 60);
                });
            }

            $scope.$watch('widget.configuration', function(config) {
                if (timeoutId) {
                    $timeout.cancel(timeoutId);
                }

                if (config) {
                    refresh(config);
                }
            }, true);

            $scope.view = function(item) {
                //superdesk.intent(superdesk.ACTION_VIEW, 'ingest', item);
            };

            $scope.$on('$destroy', function() {
                $timeout.cancel(timeoutId);
            });
        }])
        .controller('IngestConfigController', ['$scope', 'superdesk', 'api',
        function ($scope, superdesk, api) {
            api.ingest.query({source: {size: 0}}).then(function(items) {
                $scope.availableProviders = ['all'].concat(_.pluck(items._facets.provider.terms, 'term'));
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
