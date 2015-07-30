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
                thumbnail: require.toUrl('./thumbnail.svg'),
                template: require.toUrl('./widget-ingest.html'),
                configurationTemplate: 'scripts/superdesk-archive/archive-widget/configuration.html',
                configuration: {maxItems: 10, savedSearch: null, updateInterval: 5},
                description: 'Ingest widget'
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('ingest', {
                label: gettext('Ingest'),
                icon: 'ingest',
                template: require.toUrl('./widget-ingest.html'),
                order: 2,
                side: 'left',
                display: {authoring: true, packages: false}
            });
        }])
        .controller('IngestController', ['$scope', 'api', 'BaseWidgetController',
        function ($scope, api, BaseWidgetController) {
            $scope.type = 'ingestWidget';
            $scope.itemListOptions = {
                endpoint: 'search',
                repo: 'ingest',
                notStates: ['spiked'],
                types: ['text', 'picture', 'audio', 'video', 'composite'],
                page: 1
            };
            $scope.options = {
                pinEnabled: true,
                modeEnabled: true,
                searchEnabled: true,
                itemTypeEnabled: true,
                mode: 'basic',
                pinMode: 'ingest',
                similar: false,
                itemTypes: ['text', 'picture', 'audio', 'video', 'composite']
            };

            BaseWidgetController.call(this, $scope);
        }]);
});
