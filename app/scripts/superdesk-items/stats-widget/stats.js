define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.widgets.ingeststats', [])
        .config(['widgetsProvider', function(widgetsProvider) {
            widgetsProvider
                .widget('ingeststats', {
                    name: 'Ingest Stats',
                    multiple: true,
                    'class': 'ingest-stats',
                    icon: 'signal',
                    max_sizex: 1,
                    max_sizey: 1,
                    sizex: 1,
                    sizey: 1,
                    thumbnail: 'scripts/superdesk-items/stats-widget/thumbnail.png',
                    template: 'scripts/superdesk-items/stats-widget/widget-ingeststats.html',
                    configurationTemplate: 'scripts/superdesk-items/stats-widget/configuration.html',
                    configuration: {
                        source : 'provider',
                        colorScheme : 'superdesk',
                        updateInterval : 5
                    },
                    description: 'Displaying news ingest statistics. You have ability to switch color themes or graph sources.'
                });
        }])
        .controller('IngestStatsController', ['$scope', '$timeout', 'em',
        function ($scope, $timeout, em) {
            var updateData = function() {
                em.getRepository('ingest').matching().then(function(items) {
                    $scope.items = items;

                    $timeout(function() {
                        updateData();
                    }, $scope.widget.configuration.updateInterval * 1000 * 60);
                });
            };

            updateData();
        }])
        .controller('IngestStatsConfigController', ['$scope', 'colorSchemes',
        function ($scope, colorSchemes) {
            colorSchemes.get(function(colorsData) {
                $scope.schemes = colorsData.schemes;
            });
        }]);
});
