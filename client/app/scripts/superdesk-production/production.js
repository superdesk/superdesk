(function() {
    'use strict';

    ProductionController.$inject = ['$scope', 'production', 'superdesk', 'authoring', '$location', 'referrer', '$timeout'];
    function ProductionController($scope, production, superdesk, authoring, $location, referrer, $timeout) {
        var MAX_VIEW = {max: true},
            MIN_VIEW = {min: true},
            ITEM_VIEW = {medium: true},
            COMPACT_VIEW = {compact: true};

        this.view = MAX_VIEW;

        this.openItem = openItem;
        this.closeItem = closeItem;
        this.closeList = closeList;
        this.openList = openList;
        this.closeEditor = closeEditor;
        this.compactView = toggleCompactView;
        this.extendedView = toggleExtendedView;

        var vm = this,
            listView = ITEM_VIEW;

        function openItem(item) {
            vm.item = item;
            openList();
        }

        function closeItem() {
            vm.item = null;
            closeEditor();
        }

        function closeList() {
            vm.view = MIN_VIEW;
        }

        function openList() {
            vm.view = listView;
        }

        function closeEditor() {
            vm.view = MAX_VIEW;
        }

        function toggleCompactView() {
            vm.view = listView = COMPACT_VIEW;
        }

        function toggleExtendedView() {
            vm.view = listView = ITEM_VIEW;
        }

        $scope.productionPreview = true;
        $scope.selected_id = null;
        $scope.$on('itemClosing', function() {
            vm.closeItem();
        });

        $scope.$on('handleItemPreview', function(event, item) {
            referrer.setReferrerUrl($location.path());
            $scope.origItem = item;
            $scope.action = 'view';
            $scope._editable = false;
            item._editable = false;
            vm.openItem(item);

            var data = {};
            data.item = item;
            data.action = 'view';
            $scope.$root.$broadcast('showPreview', data);
        });

        $scope.$on('handleItemEdit', function(event, item) {
            referrer.setReferrerUrl($location.path());
            item._editable = true;
            $scope.origItem = item;
            $scope.action = 'view';
            $scope._editable = false;

            authoring.open(item._id, false).then(function(item) {
                var data = {};
                data.item = item;
                data.action = 'edit';
                $scope.$root.$broadcast('showPreview', data);
            })
            ['finally'](function() {
                vm.openItem(item);
            });
        });
    }

    ProductionService.$inject = ['api', '$q'];
    function ProductionService(api, $q) {
        this.items = null;
        this.fetch = function fetch(_id) {
            return api.find('archive', _id).then(function(result) {
                this.item = result;
                return result;
            });
        };
    }

    angular.module('superdesk.production', [
        'superdesk.editor',
        'superdesk.activity',
        'superdesk.authoring',
        'superdesk.authoring.widgets',
        'superdesk.desks',
        'superdesk.api'
    ])

        .service('production', ProductionService)
        .controller('Production', ProductionController)
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/workspace/production', {
                    category: '/workspace',
                    label: gettext('Production'),
                    templateUrl: 'scripts/superdesk-production/views/production.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    controller: 'Production',
                    controllerAs: 'production'
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('archive', {
                type: 'http',
                backend: {rel: 'archive'}
            });
        }]);
})();
