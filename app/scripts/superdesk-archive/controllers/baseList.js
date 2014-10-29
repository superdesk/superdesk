define(['lodash'], function(_) {
    'use strict';

    BaseListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es', 'preferencesService', 'notify'];
    function BaseListController($scope, $location, superdesk, api, es, preferencesService, notify) {
        var self = this;

        var lastQueryParams = {};
        var savedView;
        preferencesService.get('archive:view').then(function(result) {
            savedView = result.view;
            $scope.view = (!!savedView && savedView !== 'undefined') ? savedView : 'mgrid';
        });

        $scope.selected = {};

        $scope.setView = function(view) {

            var update = {
                'archive:view': {
                    'allowed': [
                        'mgrid',
                        'compact'
                    ],
                    'category': 'archive',
                    'view': view || 'mgrid',
                    'default': 'mgrid',
                    'label': 'Users archive view format',
                    'type': 'string'
                }
            };

            preferencesService.update(update, 'archive:view').then(function() {
                    $scope.view = view || 'mgrid';
                }, function(response) {
                    notify.error(gettext('User preference could not be saved...'));
            });
        };

        $scope.preview = function(item) {
            $scope.selected.preview = item;
            $location.search('_id', item ? item._id : null);
        };

        $scope.display = function() {
            $scope.selected.view = $scope.selected.preview;
        };

        $scope.$watchCollection(function() {
            return _.omit($location.search(), '_id');
        }, function(search) {
            var query = self.getQuery(search);
            self.fetchItems({source: query});
        });

        $scope.$watch(function() {
            return $location.search()._id || null;
        }, function(id) {
            if (!id) {
                $scope.selected.preview = null;
            }
        });

        this.buildFilters = function(params) {
            var filters = [];

            if (params.before || params.after) {
                var range = {versioncreated: {}};
                if (params.before) {
                    range.versioncreated.lte = params.before;
                }

                if (params.after) {
                    range.versioncreated.gte = params.after;
                }

                filters.push({range: range});
            }

            if (params.provider) {
                var provider = {
                    provider: params.provider
                };
                filters.push({term: provider});
            }

            if (params.type) {
                var type = {
                    type: JSON.parse(params.type)
                };
                filters.push({terms: type});
            }

            if (params.urgency_min || params.urgency_max) {
                params.urgency_min = params.urgency_min || 1;
                params.urgency_max = params.urgency_max || 5;
                var urgency = {
                    urgency: {
                        gte: params.urgency_min,
                        lte: params.urgency_max
                    }
                };
                filters.push({range: urgency});
            }

            return filters;
        };

        this.getQuery = function(params) {
            if (!_.isEqual(_.omit(params, 'page'), _.omit(lastQueryParams, 'page'))) {
                $location.search('page', null);
            }
            var filters = this.buildFilters(params);
            var query = es(params, filters);
            query.sort = [{versioncreated: 'desc'}];
            lastQueryParams = params;
            return query;
        };

        this.fetchItems = function(criteria) {
            console.log('no api defined');
        };

        this.refresh = function() {
        	var query = self.getQuery(_.omit($location.search(), '_id'));
            self.fetchItems({source: query});
        };
    }

    return BaseListController;
});
