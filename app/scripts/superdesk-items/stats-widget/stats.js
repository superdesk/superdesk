define([
    'angular',
    'superdesk-dashboard/services'
], function(angular) {
    'use strict';

    angular.module('superdesk.widgets.ingeststats', ['superdesk.dashboard.services'])
        .config(['widgetsProvider', function(widgetsProvider) {
            widgetsProvider
                .widget('ingeststats', {
                    name: 'Ingest Stats',
                    multiple: true,
                    class: 'ingest-stats',
                    icon: 'signal',
                    max_sizex: 1,
                    max_sizey: 1,
                    sizex: 1,
                    sizey: 1,
                    thumbnail: 'scripts/superdesk-items/stats-widget/thumbnail.png',
                    template: 'scripts/superdesk-items/stats-widget/widget-ingeststats.html',
                    configurationTemplate: 'scripts/superdesk-items/stats-widget/configuration.html',
                    configuration: {
                        sourceno : 1,
                        colorScheme : 'superdesk',
                        updateInterval : 5
                    },
                    description: 'Displaying news ingest statistics. You have ability to switch color themes or graph sources.'
                });
        }])
        .controller('IngestStatsController', ['$scope', '$timeout', 'em',
        function ($scope, $timeout, em) {
            var update = function() {
                em.getRepository('ingest').matching().then(function(items) {
                    
                    switch(parseInt($scope.widget.configuration.sourceno,10)) {
                    case 1 :
                        $scope.chartSource = items._facets.provider.terms;
                        break;
                    case 2 :
                        $scope.chartSource = items._facets.urgency.terms;
                        break;
                    case 3 :
                        $scope.chartSource = items._facets.subject.terms;
                        break;
                    }

                    $timeout(function() {
                        update();
                    }, $scope.widget.configuration.updateInterval * 1000 * 60);
                });
                
                $scope.chartColor = $scope.widget.configuration.colorScheme;
            };

           
            $scope.$watch('widget.configuration', function() {
                update();
            }, true);

            update();

        }])
        .controller('IngestStatsConfigController', ['$scope', 'colorSchemes',
        function ($scope, colorSchemes) {
            colorSchemes.get(function(colorsData) {
                $scope.schemes = colorsData.schemes;
            });
        }]);
});
