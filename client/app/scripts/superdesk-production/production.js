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

        $scope.$on('handlePreview', function(event, arg) {
            $scope.origItem = arg;
            $scope.selected_id = arg._id;
            $scope.action = 'view';
            $scope._editable = null;
            $scope.viewdefault = false;
        });
        $scope.$on('handleEdit', function(event, arg) {
            $scope.origItem = arg;
            $scope.selected_id = arg._id;
            $scope.action = 'edit';
            $scope._editable = $scope.origItem._editable;
            $scope.viewdefault = false;
        });
        $scope.$on('openProductionArticle', function(event, arg) {
            referrer.setReferrerUrl($location.url());
            $scope.origItem = arg;
            $scope.selected_id = arg._id;
            $scope.action = 'view';
            $scope._editable = null;
            $scope.viewdefault = false;
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
