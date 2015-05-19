(function() {
    'use strict';

    ProductionController.$inject = ['$scope', 'production', 'superdesk', 'authoring', '$location', 'referrer'];
    function ProductionController($scope, production, superdesk, authoring, $location, referrer) {
        $scope.productionPreview = true;
        $scope.origItem = {};
        $scope.action = 'view';
        $scope.viewdefault = true;
        $scope.selected_id = null;
        $scope.items = {};
        $scope.$on('itemClosing', function() {
            $scope.viewdefault = true;
        });

        $scope.$on('handleItemPreview', function(event, item) {
            referrer.setReferrerUrl($location.path());
            $scope.origItem = item;
            $scope.selected_id = item._id;
            $scope.action = 'view';
            $scope._editable = null;
            $scope.viewdefault = false;
        });
        $scope.$on('handleItemEdit', function(event, item) {
            referrer.setReferrerUrl($location.path());
            item._editable = true;
            authoring.open(item._id, false).then(function(item) {
                $scope.origItem = item;
                $scope.action = 'edit';
                $scope.origItem._editable = true;
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
