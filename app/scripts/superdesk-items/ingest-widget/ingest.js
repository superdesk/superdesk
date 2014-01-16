define([
    'angular'
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
                    thumbnail: 'scripts/superdesk-items/ingest-widget/thumbnail.png',
                    template: 'scripts/superdesk-items/ingest-widget/widget-ingest.html',
                    configurationTemplate: 'scripts/superdesk-items/ingest-widget/configuration.html',
                    configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                    description: 'Ingest widget'
                });
        }])
        .controller('IngestController', ['$scope', '$timeout', 'em', 'superdesk',
        function ($scope, $timeout, em, superdesk) {
            function update() {
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

                em.getRepository('ingest').matching(criteria).then(function(items) {
                    $scope.items = items;

                    $timeout(function() {
                        update();
                    }, $scope.widget.configuration.updateInterval * 1000 * 60);
                });
            }

            $scope.$watch('widget.configuration', function() {
                update();
            }, true);

            $scope.preview = function(item) {
                superdesk.intent(superdesk.ACTION_PREVIEW, 'ingest', item);
            };
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
