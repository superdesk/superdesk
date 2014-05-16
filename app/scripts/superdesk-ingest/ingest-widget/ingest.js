define([
    'angular',
    'require'
], function(angular) {
    'use strict';

    angular.module('superdesk.widgets.ingest', [])
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .widget('ingest', {
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
        .controller('IngestController', ['$scope', '$timeout', 'superdesk',
        function ($scope, $timeout, superdesk) {
            var timeoutId;

            $scope.items = superdesk.data('ingest');

            function refresh(config) {
                var criteria = {
                    sort: ['versioncreated', 'desc'],
                    max_results: config.maxItems,
                    q: config.search !== '' ? config.search : null
                };

                $scope.items.query(criteria).then(function() {
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

            $scope.preview = function(item) {
                superdesk.intent(superdesk.ACTION_PREVIEW, 'ingest', item);
            };

            $scope.$on('$destroy', function() {
                $timeout.cancel(timeoutId);
            });
        }])
        .controller('IngestConfigController', ['$scope', 'superdesk',
        function ($scope, superdesk) {
            var ingest = superdesk.data('ingest');
            ingest.query({max_results: 0}).then(function(items) {
                $scope.availableProviders = ['all'].concat(_.pluck(items._facets.provider.terms, 'term'));
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
