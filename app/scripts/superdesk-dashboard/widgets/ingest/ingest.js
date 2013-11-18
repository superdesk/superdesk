define([
    'angular'
], function(angular) {
    'use strict';

    angular.module('superdesk.widgets.ingest', [])
        .config(['widgetsProvider', function(widgetsProvider) {
            widgetsProvider
                .widget('ingest', {
                    name: 'Ingest',
                    class: 'ingest',
                    icon: 'time',
                    max_sizex: 2,
                    max_sizey: 1,
                    sizex: 1,
                    sizey: 1,
                    thumbnail: 'images/sample/widgets/worldclock.png',
                    template: 'scripts/superdesk-dashboard/widgets/ingest/widget-ingest.html',
                    configurationTemplate: 'scripts/superdesk-dashboard/widgets/ingest/configuration.html',
                    configuration: {maxItems: 10, providers: [], search: ''},
                    description: 'Ingest widget'
                });
        }])
        .controller('IngestController', ['$scope', 'em',
        function ($scope, em) {
            $scope.sizey = $scope.widget.sizey;

            var criteria = {
                sort: ['firstcreated', 'desc'],
                max_results: $scope.widget.configuration.maxItems,
                page: 1,
                q: $scope.widget.configuration.search !== '' ? $scope.widget.configuration.search : undefined,
                where: {
                    provider: $scope.widget.configuration.providers.length ? $scope.widget.configuration.providers : undefined
                }
            };

            em.getRepository('ingest').matching(criteria).then(function(items) {
                $scope.items = items;
            });


        }])
        .controller('IngestConfigController', ['$scope', 'em',
        function ($scope, em) {
            em.getRepository('ingest').matching({max_results: 0}).then(function(items) {
                $scope.availableProviders = _.pluck(items._facets.provider.terms, 'term');
                if ($scope.configuration.providers.length === 0) {
                    $scope.configuration.providers = angular.extend([], $scope.availableProviders);
                }
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
