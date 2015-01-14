define([
    'angular',
    'require',
    './baseWidget'
], function(angular, require) {
    'use strict';

    angular.module('superdesk.widgets.archive', [
        'superdesk.widgets.base',
        'superdesk.authoring.widgets'
    ])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('archive', {
                label: 'Archive',
                multiple: true,
                icon: 'archive',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.png'),
                template: require.toUrl('./widget-archive.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 10, provider: 'all', search: '', updateInterval: 5},
                description: 'Archive widget'
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('archive', {
                label: gettext('Archive'),
                icon: 'archive',
                template: require.toUrl('./widget-archive.html'),
                side: 'left'
            });
        }])
        .controller('ArchiveController', ['$scope', 'api', 'BaseWidgetController',
        function ($scope, api, BaseWidgetController) {
            $scope.type = 'archiveWidget';
            $scope.api = api.archive;

            BaseWidgetController.call(this, $scope);
        }])
        .controller('ArchiveConfigController', ['$scope', 'api', 'BaseWidgetConfigController',
        function ($scope, api, BaseWidgetConfigController) {
            $scope.api = api.archive;

            BaseWidgetConfigController.call(this, $scope);

            $scope.fetchProviders();
        }]);
});
