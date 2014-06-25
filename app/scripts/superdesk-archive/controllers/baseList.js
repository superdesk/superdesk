define(['lodash'], function(_) {
    'use strict';

    BaseListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'es'];
    function BaseListController($scope, $location, superdesk, api, es) {
        var self = this;

        $scope.view = 'mgrid';
        $scope.selected = {};

        $scope.preview = function(item) {
            $scope.selected.preview = item;
            $location.search('_id', item ? item._id : null);
        };

        $scope.display = function(item) {
            $scope.selected.view = item;
        };

        $scope.$watchCollection(function() {
            return _.omit($location.search(), '_id');
        }, function(search) {
            var query = self.getQuery(search);
            self.fetchItems({source: query});
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
            var filters = this.buildFilters(params);
            var query = es(params, filters);
            query.sort = [{versioncreated: 'desc'}];
            return query;
        };

        this.fetchItems = function(criteria) {
            console.log('no api defined');
        };
    }

    return BaseListController;
});
