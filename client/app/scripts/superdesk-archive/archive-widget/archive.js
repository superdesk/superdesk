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
                label: 'Content',
                multiple: true,
                icon: 'archive',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: require.toUrl('./thumbnail.svg'),
                template: require.toUrl('./widget-archive.html'),
                configurationTemplate: require.toUrl('./configuration.html'),
                configuration: {maxItems: 10, savedSearch: null, updateInterval: 5},
                description: 'Content widget'
            });
        }])
        .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('archive', {
                label: gettext('Content'),
                icon: 'archive',
                template: require.toUrl('./widget-archive.html'),
                order: 3,
                side: 'left',
                display: {authoring: true, packages: false}
            });
        }])
        .controller('ArchiveController', ['$scope', 'api', 'BaseWidgetController', '$location',
        function ($scope, api, BaseWidgetController, $location) {
            $scope.type = 'archiveWidget';
            $scope.itemListOptions = {
                endpoint: 'search',
                repo: 'archive',
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
                pinMode: 'archive',
                similar: false,
                itemTypes: ['text', 'picture', 'audio', 'video', 'composite']
            };
            $scope.actions = {
                open: {
                    title: 'Open',
                    method: function(item) {
                        if (!sessionStorage.getItem('previewUrl')) {
                            sessionStorage.setItem('previewUrl', $location.url());
                        }
                        $location.path('/authoring/' + item._id + '/view');
                    },
                    'class': 'open',
                    icon: 'icon-pencil'
                }
            };

            BaseWidgetController.call(this, $scope);
        }]);
});
