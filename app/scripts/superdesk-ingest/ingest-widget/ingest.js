define([
    'angular',
    'require',
    'superdesk-archive/archive-widget/baseWidget'
], function(angular, require, BaseWidget) {
    'use strict';

    angular.module('superdesk.widgets.ingest', [
        'superdesk.widgets.base',
        'superdesk.authoring.widgets'
    ])
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
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('ingest', {
                label: gettext('Ingest'),
                icon: 'ingest',
                template: require.toUrl('./widget-ingest.html'),
                side: 'left'
            });
        }])
        .controller('IngestController', ['$scope', 'api', 'BaseWidgetController',
        function ($scope, api, BaseWidgetController) {
            $scope.type = 'ingestWidget';
            $scope.api = api.ingest;

            BaseWidgetController.call(this, $scope);
        }])
        .controller('IngestConfigController', ['$scope', 'api', 'BaseWidgetConfigController',
        function ($scope, api, BaseWidgetConfigController) {
            $scope.api = api.ingest;

            BaseWidgetConfigController.call(this, $scope);

            $scope.fetchProviders();
        }]);
});
