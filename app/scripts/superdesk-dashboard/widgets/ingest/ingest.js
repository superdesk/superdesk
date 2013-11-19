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
                    max_sizey: 2,
                    sizex: 1,
                    sizey: 2,
                    thumbnail: 'images/sample/widgets/worldclock.png',
                    template: 'scripts/superdesk-dashboard/widgets/ingest/widget-ingest.html',
                    configurationTemplate: 'scripts/superdesk-dashboard/widgets/ingest/configuration.html',
                    configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                    description: 'Ingest widget'
                });
        }])
        .controller('IngestController', ['$scope', '$timeout', 'em',
        function ($scope, $timeout, em) {
            $scope.size = {
                x: $scope.widget.sizex,
                y: $scope.widget.sizey
            };

            var criteria = {
                sort: ['versioncreated', 'desc'],
                max_results: $scope.widget.configuration.maxItems,
                page: 1,
                q: $scope.widget.configuration.search !== '' ? $scope.widget.configuration.search : undefined
            };

            if ($scope.widget.configuration.provider !== 'all') {
                criteria.where = {
                    provider: $scope.widget.configuration.provider
                };
            }

            var update = function() {
                em.getRepository('ingest').matching(criteria).then(function(items) {
                    $scope.items = items;
                });
                $timeout(function() {
                    update();
                }, $scope.widget.configuration.updateInterval * 1000 * 60);
            };

            $scope.compileSubjects = function(subjects) {
                return _.pluck(subjects, 'name').join(', ');
            };

            update();
        }])
        .controller('IngestConfigController', ['$scope', 'em',
        function ($scope, em) {
            em.getRepository('ingest').matching({max_results: 0}).then(function(items) {
                $scope.availableProviders = ['all'].concat(_.pluck(items._facets.provider.terms, 'term'));
            });

            $scope.notIn = function(haystack) {
                return function(needle) {
                    return haystack.indexOf(needle) === -1;
                };
            };
        }]);
});
