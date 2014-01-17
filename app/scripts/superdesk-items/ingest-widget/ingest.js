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
        .controller('IngestController', ['$scope', 'superdesk',
        function ($scope, superdesk) {
            $scope.items = superdesk.data('ingest');

            $scope.$watch('widget.configuration', function(config) {
                var criteria = {
                    sort: ['versioncreated', 'desc'],
                    max_results: config.maxItems,
                    q: config.search !== '' ? config.search : null,
                    ttl: config.updateInterval * 1000 //* 60
                };

                $scope.items.reset(criteria);
            }, true);

            $scope.preview = function(item) {
                superdesk.intent(superdesk.ACTION_PREVIEW, 'ingest', item);
            };
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
