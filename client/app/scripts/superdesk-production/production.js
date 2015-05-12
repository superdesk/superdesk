(function() {
'use strict';

ProductionController.$inject = ['$scope', 'production', 'superdesk', 'authoring'];
function ProductionController($scope, production, superdesk, authoring) {
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
/*ProductionController.$inject = ['$scope'];
function ProductionController($scope) {
        $scope.origItem = item;
        $scope.action = action || 'edit';

        $scope.widget_target = 'authoring';

        $scope.intentFilter = {
            action: 'author',
            type: 'article'
        };
    }*/

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

    /*AggregateWidgetCtrl.$inject = ['desks', 'preferencesService'];
    function AggregateWidgetCtrl(desks, preferencesService) {

        var PREFERENCES_KEY = 'agg:view';

        this.configured = false;
        this.selected = null;
        this.active = {};

        this.setConfigured = function() {
            this.configured = _.keys(this.active).length > 0;
        };

        desks.initialize()
        .then(angular.bind(this, function() {
            return preferencesService.get(PREFERENCES_KEY)
                .then(angular.bind(this, function(active) {
                    this.active = active != null ? active.active : {};
                    this.setConfigured();
                }));
        }))
        .then(angular.bind(this, function() {
            return desks.fetchCurrentUserDesks()
                .then(angular.bind(this, function (deskList) {
                    this.desks = deskList;
                    this.deskStages = desks.deskStages;
                }));
        }));

        this.preview = function(item) {
            this.selected = item;
        };

        this.closeModal = function() {
            this.modalActive = false;
        };

        this.edit = function() {
            this.oldActive = this.active;
            this.active = _.create(this.active);
            this.modalActive = true;
        };

        this.cancel = function() {
            this.active = this.oldActive;
            this.closeModal();
        };

        this.isActive = angular.bind(this, function(item) {
            if (this.searchAll || !this.configured) {
                return true;
            }

            return !!this.active[item._id];
        });

        this.save = function() {
            var updates = {};
            updates[PREFERENCES_KEY] = {active: this.active};
            preferencesService.update(updates, PREFERENCES_KEY)
                .then(angular.bind(this, function() {
                    this.setConfigured();
                    this.closeModal();
                }));
        };

        this.search = function(query) {
            this.query = query;
        };

        this.searchAll = false;
    }*/

return angular.module('superdesk.production', [
        'superdesk.editor',
        'superdesk.activity',
        'superdesk.authoring',
        'superdesk.authoring.widgets',
        'superdesk.desks',
        'superdesk.api'
    ])
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
})();
