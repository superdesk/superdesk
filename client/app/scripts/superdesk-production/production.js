(function() {
'use strict';

ProductionController.$inject = ['$scope', 'production', 'superdesk', 'authoring'];
function ProductionController($scope, production, superdesk, authoring) {
        $scope.productionPreview = true;
        $scope.origItem = {};
        $scope.action = 'view';
        $scope.viewdefault = _.isEqual({}, $scope.origItem) ? true : false;

        $scope.items = {};

        $scope.$on('handlePreview', function(event, arg) {
            //$scope.$apply(function() {
            console.log('event broadcast');
            //$scope.origItem =  arg;
            console.log(arg._id);
            //});
            authoring.open(arg._id, true).
                then(function(opened) {
                    $scope.origItem = opened;
                    $scope.items = opened;
                    //scope.$parent.items = opened;
                    //scope.$emit('handlePreview', opened);
                    console.log('Inside production controller');
                });
        });

        $scope.$watch($scope.origItem, function() {
                console.log('production Ctrl');
            });

        //$scope._editable = true;
        /*$scope.items = null;
        production.query().then(function() {
            $scope.items = production.items;
        });

        $scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.widget_target = 'production';
        $scope._editable = scope.origItem._editable;

        $scope.intentFilter = {
            action: 'author',
            type: 'article'
        };*/
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
        /*this.query = function() {
            var criteria = getCriteria();
            return api.production.query(criteria)
                .then(angular.bind(this, function(items) {
                this.items = items;
                return this.items;
            }));
        };*/

        //return items;
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
            /*.activity('read_only.content_article', {
                category: '/production',
                href: '/production/:_id/view',
                when: '/production/:_id/view',
                label: gettext('Production Read Only'),
                templateUrl: 'scripts/superdesk-production/views/production.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                controller: ProductionController,
                filters: [{action: 'read_only', type: 'content_article'}],
                resolve: {
                    item: ['$route', 'authoring', function($route, authoring) {
                        return authoring.open($route.current.params._id, true);
                    }],
                    action: [function() {return 'view';}]
                },
                authoring: true
            });*/
/*            .activity('edit.text', {
                label: gettext('Edit item'),
                href: '/production/:_id',
                priority: 10,
                icon: 'pencil',
                controller: ['data', 'superdesk', function(data, superdesk) {
                    superdesk.intent('producer', 'article', data.item);
                }],
                filters: [{action: 'list', type: 'archive'}],
                condition: function(item) {
                    return item.type !== 'composite' &&
                    item.state !== 'published' &&
                    item.state !== 'scheduled' &&
                    item.state !== 'killed';
                }
            });*/
    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('archive', {
            type: 'http',
            backend: {rel: 'archive'}
        });
    }]);
    /*.config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('aggregate', {
                icon: 'view',
                label: gettext('Aggregate'),
                template: 'scripts/superdesk-desks/views/aggregate-widget.html',
                side: 'right',
                extended: true,
                display: {authoring: true, packages: false, production: true}
            });
    }]);*/
    //.controller('AggregateWidgetCtrl', AggregateWidgetCtrl);

return prod;
})();
