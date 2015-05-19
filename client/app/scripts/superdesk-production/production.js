(function() {
    'use strict';

    ProductionController.$inject = ['$scope', 'production', 'superdesk', 'authoring', '$location', 'referrer', '$timeout'];
    function ProductionController($scope, production, superdesk, authoring, $location, referrer, $timeout) {
        $scope.productionPreview = true;
        $scope.viewdefault = true;
        $scope.selected_id = null;
        $scope.$on('itemClosing', function() {
            $scope.viewdefault = true;
        });

        $scope.$on('handleItemPreview', function(event, item) {
            referrer.setReferrerUrl($location.path());
            $scope.origItem = item;
            $scope.action = 'view';
            $scope._editable = false;
            $scope.viewdefault = false;
            item._editable = false;

            var data = {};
            data.item = item;
            data.action = 'view';
            $scope.viewdefault = false;
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
                $scope.viewdefault = false;
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
    var prod =  angular.module('superdesk.production', [
        'superdesk.editor',
        'superdesk.activity',
        'superdesk.authoring',
        'superdesk.authoring.widgets',
        'superdesk.desks',
        'superdesk.api'
    ]);

    prod
        .service('production', ProductionService)
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/workspace/production', {
                    category: '/workspace',
                    label: gettext('Production'),
                    templateUrl: 'scripts/superdesk-production/views/production.html',
                    topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                    controller: ProductionController
                });
        }])
        .config(['apiProvider', function(apiProvider) {
            apiProvider.api('archive', {
                type: 'http',
                backend: {rel: 'archive'}
            });
        }]);
    return prod;
})();
