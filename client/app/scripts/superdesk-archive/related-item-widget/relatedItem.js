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
                icon: 'related',
                template: require.toUrl('./widget-relatedItem.html'),
                order: 7,
                side: 'right',
                display: {authoring: true, packages: false, legalArchive: false}
            });
        }])
        .controller('relatedItemController',
        ['$scope', 'api', 'BaseWidgetController', '$location', 'notify', 'superdesk',
        function ($scope, api, BaseWidgetController, $location, notify, superdesk) {
            var before24HrDateTime = moment().subtract(1, 'days').format();
            $scope.type = 'archiveWidget';
            $scope.itemListOptions = {
                endpoint: 'search',
                repo: ['archive', 'published'],
                notStates: ['spiked'],
                types: ['text', 'picture', 'audio', 'video'],
                page: 1,
                modificationDateAfter: before24HrDateTime
            };
            $scope.options = {
                pinEnabled: true,
                modeEnabled: true,
                searchEnabled: true,
                itemTypeEnabled: true,
                mode: 'basic',
                pinMode: 'archive',
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
                        */

                        $scope.origItem = $scope.options.item;
                        $scope.options.item.subject = item.subject;
                        $scope.options.item.anpa_category = item.anpa_category;
                        $scope.options.item.headline = item.headline;
                        $scope.options.item.urgency = item.urgency;
                        $scope.options.item.priority = item.priority;
                        $scope.options.item.slugline = item.slugline;
                        $scope.options.item.related_to = item._id;
                        api.save('archive', $scope.origItem, $scope.options.item).then(function(_item) {
                            notify.success(gettext('item updated.'));
                            return item;
                        });
                    },
                    'class': 'open',
                    icon: 'icon-expand'
                },
                open: {
                    title: 'Open',
                    method: function(item) {
                        superdesk.intent('edit', 'item', item);
                    },
                    'class': 'open',
                    icon: 'icon-external'
                }
            };
            BaseWidgetController.call(this, $scope);
        }]);
});
