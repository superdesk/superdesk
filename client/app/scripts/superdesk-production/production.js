(function() {
'use strict';

/*ProductionController.$inject = ['$scope', 'item', 'action'];
function ProductionController($scope, item, action) {
        $scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.widget_target = 'authoring';

        $scope.intentFilter = {
            action: 'author',
            type: 'article'
        };
    }*/
ProductionController.$inject = ['$scope'];
function ProductionController($scope) {
        /*$scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.widget_target = 'authoring';

        $scope.intentFilter = {
            action: 'author',
            type: 'article'
        };*/
    }

return angular.module('superdesk.production', [
        'superdesk.editor',
        'superdesk.activity',
        'superdesk.authoring',
        'superdesk.authoring.widgets',
        'superdesk.desks'
    ])
    .config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/workspace/production', {
                category: '/workspace',
                label: gettext('Production'),
                templateUrl: 'scripts/superdesk-production/views/production.html',
                topTemplateUrl: 'scripts/superdesk-dashboard/views/workspace-topnav.html',
                controller: ProductionController
            });
           /* .activity('edit.text', {
                label: gettext('Edit item'),
                href: '/production/:_id',
                priority: 10,
                icon: 'pencil',
                controller: ['data', 'superdesk', function(data, superdesk) {
                    superdesk.intent('author', 'article', data.item);
                }],
                filters: [{action: 'list', type: 'archive'}],
                condition: function(item) {
                    return item.type !== 'composite' &&
                    item.state !== 'published' &&
                    item.state !== 'scheduled' &&
                    item.state !== 'killed';
                }
            })
            .activity('read_only.content_article', {
                category: '/production',
                href: '/production/:_id/view',
                when: '/production/:_id/view',
                label: gettext('Authoring Read Only'),
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
    }]);
})();
