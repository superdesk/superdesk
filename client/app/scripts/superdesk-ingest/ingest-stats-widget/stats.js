(function() {
    'use strict';

    angular.module('superdesk.widgets.ingeststats', [])
        .factory('colorSchemes', ['$resource', function($resource) {
            return $resource('scripts/superdesk-ingest/static-resources/color-schemes.json');
        }])
        .config(['dashboardWidgetsProvider', function(dashboardWidgets) {
            dashboardWidgets.addWidget('ingest-stats', {
                label: 'Ingest Stats',
                multiple: true,
                icon: 'signal',
                max_sizex: 1,
                max_sizey: 1,
                sizex: 1,
                sizey: 1,
                thumbnail: 'scripts/superdesk-ingest/ingest-stats-widget/thumbnail.svg',
                template: 'scripts/superdesk-ingest/ingest-stats-widget/widget-ingeststats.html',
                configurationTemplate: 'scripts/superdesk-ingest/ingest-stats-widget/configuration.html',
                configuration: {
                    source: 'provider',
                    colorScheme: 'superdesk',
                    updateInterval: 5
                },
                description: 'Displaying news ingest statistics. You have ability to switch color themes or graph sources.'
            });
        }])
        .controller('IngestStatsController', ['$scope', '$timeout', 'api',
        function ($scope, $timeout, api) {
            function updateData() {
                api.ingest.query().then(function(items) {
                    $scope.items = items;

                    $timeout(function() {
                        updateData();
                    }, $scope.widget.configuration.updateInterval * 1000 * 60);
                });
            }

            updateData();
        }])
        .controller('IngestStatsConfigController', ['$scope', 'colorSchemes',
        function ($scope, colorSchemes) {
            colorSchemes.get(function(colorsData) {
                $scope.schemes = colorsData.schemes;
            });
        }]);
})();
