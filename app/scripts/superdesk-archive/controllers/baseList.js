define(['lodash'], function(_) {
    'use strict';

    BaseListController.$inject = ['$scope', '$location', 'superdesk', 'api', 'search', 'desks', 'preferencesService', 'notify'];
    function BaseListController($scope, $location, superdesk, api, search, desks, preferencesService, notify) {
        var self = this;

        var lastQueryParams = {};

        $scope.selected = {};

        $scope.openLightbox = function openLightbox() {
            $scope.selected.view = $scope.selected.preview;
        };

        $scope.closeLightbox = function closeLightbox() {
            $scope.selected.view = null;
        };

        $scope.$on('$routeUpdate', function(e, data) {
            if (!$location.search()._id) {
                $scope.selected.preview = null;
            }
        });

        this.buildQuery = function(params, filterDesk) {

            var query = search.query(params.q || null);

            if (filterDesk) {
                if (desks.getCurrentStageId()) {
                    query.filter({term: {'task.stage': desks.getCurrentStageId()}});
                } else if (desks.getCurrentDeskId()) {
                    query.filter({term: {'task.desk': desks.getCurrentDeskId()}});
                }
            }

            if (params.before || params.after) {
                var range = {versioncreated: {}};
                if (params.before) {
                    range.versioncreated.lte = params.before;
                }

                if (params.after) {
                    range.versioncreated.gte = params.after;
                }

                query.filter({range: range});
            }

            if (params.provider) {
                query.filter({term: {provider: params.provider}});
            }

            if (params.type) {
                var type = {
                    type: JSON.parse(params.type)
                };
                query.filter({terms: type});
            }

            console.log("baselist urgency:", params.urgency_min, params.urgency_max)

            if (params.urgency_min || params.urgency_max) {
                params.urgency_min = params.urgency_min || 1;
                params.urgency_max = params.urgency_max || 5;
                var urgency = {
                    urgency: {
                        gte: params.urgency_min,
                        lte: params.urgency_max
                    }
                };
                query.filter({range: urgency});
            }

            return query.getCriteria();
        };

        this.getQuery = function getQuery(params, filterDesk) {
            if (!_.isEqual(_.omit(params, 'page'), _.omit(lastQueryParams, 'page'))) {
                $location.search('page', null);
            }
            var query = this.buildQuery(params, filterDesk);
            lastQueryParams = params;
            return query;
        };

        this.fetchItems = function(criteria) {
            console.log('no api defined');
        };

        this.refresh = function refresh(filterDesk) {
        	var query = self.getQuery(_.omit($location.search(), '_id'), filterDesk);
            self.fetchItems({source: query});
        };
    }

    return BaseListController;
});
