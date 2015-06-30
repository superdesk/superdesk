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
                display: {authoring: true, packages: false}
            });
        }])
        .controller('relatedItemController', ['$scope', 'api', 'BaseWidgetController', '$location', 'notify',
        function ($scope, api, BaseWidgetController, $location, notify) {
            var before24HrDateTime = moment().subtract(1, 'days').format();
            $scope.type = 'archiveWidget';
            $scope.itemListOptions = {
                endpoint: 'search',
                repo: 'archive',
                notStates: ['spiked'],
                types: ['text', 'picture', 'audio', 'video', 'composite'],
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
                        $scope.options.item['anpa-category'] = item['anpa-category'];
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
                        $location.path('/authoring/' + item._id + '/view');
                    },
                    'class': 'open',
                    icon: 'icon-external'
                }
            };
            BaseWidgetController.call(this, $scope);
        }]);
});
