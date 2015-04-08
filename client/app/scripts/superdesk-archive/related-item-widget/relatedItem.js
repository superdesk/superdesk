define([
    'angular',
    'require',
    'moment',
    'superdesk-archive/archive-widget/baseWidget'
], function(angular, require, moment) {
    'use strict';

    angular.module('superdesk.widgets.relatedItem', [
        'superdesk.widgets.base',
        'superdesk.authoring.widgets'
    ])
    .config(['authoringWidgetsProvider', function(authoringWidgets) {
            authoringWidgets.widget('related-item', {
                label: gettext('Related Item'),
                icon: 'multiedit',
                template: require.toUrl('./widget-relatedItem.html'),
                side: 'right',
                display: {authoring: true, packages: false}
            });
        }])
        .controller('relatedItemController', ['$scope', 'api', 'BaseWidgetController', '$location',
        function ($scope, api, BaseWidgetController, $location) {
            var todayDateTime = new Date();
            var before24HrDateTime = new Date(todayDateTime.setDate(todayDateTime.getDate() - 1)).toISOString();

            $scope.type = 'archiveWidget';
            $scope.itemListOptions = {
                endpoint: 'search',
                repo: 'archive',
                notStates: ['spiked'],
                types: ['text', 'picture', 'audio', 'video', 'composite'],
                page: 1,
                creationDateAfter: before24HrDateTime
            };
            $scope.options = {
                searchEnabled: true,
                related: true,
                itemTypes: ['text', 'picture', 'audio', 'video', 'composite']
            };
            $scope.actions = {
                apply: {
                    title: 'Associate',
                    method: function(item) {
                        /*TODOs:
                        1) Overwrite Destination code
                        2) Patch IPTC Code
                        3) Overwrite category, service and locator fields
                        4) Establish a main-story-to-sidebar association (based on guid)
                        */

                        $scope.origItem = $scope.options.item;
                        $scope.options.item.subject = item.subject;
                        $scope.options.item['anpa-category'] = item['anpa-category'];
                        api.save('archive', $scope.origItem, $scope.options.item).then(function(_item) {
                            return item;
                        });
                    },
                    'class': 'open',
                    icon: 'icon-expand'
                },
                open: {
                    title: 'Open',
                    method: function(item) {
                        $location.path('/authoring/' + item._id + '/view');
                    },
                    'class': 'open',
                    icon: 'icon-expand'
                }
            };
            BaseWidgetController.call(this, $scope);
        }]);
});
