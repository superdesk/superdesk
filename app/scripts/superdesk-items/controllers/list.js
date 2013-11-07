define(['lodash', 'angular'], function(_, angular) {
    'use strict';

    return ['$scope', '$routeParams', 'items', 'storage', 'em', 'notify', 'gettext',
    function($scope, $routeParams, items, storage, em, notify, gettext) {

        function getSetting(key, def) {
            var val = storage.getItem(key);
            return (val === null) ? def : val;
        }

        $scope.items = items;

        $scope.selectedItem = {
            item: items._items[0],
            position: {
                left: 0,
                top: 0
            },
            show: false
        };

        $scope.ui = {
            compact: getSetting('archive:compact', false),
            grid: getSetting('archive:grid', true)
        };

        $scope.toggleCompact = function() {
            $scope.ui.compact = !$scope.ui.compact;
            storage.setItem('archive:compact', $scope.ui.compact, true);
        };

        $scope.setGridView = function(val) {
            $scope.ui.grid = !!val;
            storage.setItem('archive:grid', $scope.ui.grid, true);
        };

        $scope.edit = function(item) {
            $scope.editItem = item;
        };

        $scope.closeEdit = function() {
            $scope.editItem = null;
        };

        $scope.archive = function(item) {
            notify.info(gettext('Saving item..'));
            em.create('archive', item).then(function() {
                notify.pop();
                notify.success(gettext('Item archived!'), 3000);
            });
        };
    }];
});
