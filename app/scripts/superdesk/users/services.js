define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.users.services', []).
        service('converter', ['defaultListParams', function(defaultListParams) {
            return new function() {
                this.convert = function(params) {
                    params = angular.extend({}, defaultListParams, params);
                    var result = {
                        page: params.page,
                        max_results: params.perPage
                    };
                    var sortDirection = 1;
                    if (params.sortDirection === 'desc') {
                        sortDirection = -1;
                    }
                    result.sort = '[("' + params.sortField + '", ' + sortDirection + ')]';
                    if (params.search !== '') {
                        // TODO (ozan): display_name should be used, after server starts to provide it.
                        // result.where = angular.toJson({display_name: params.search});
                        result.where = angular.toJson({username: params.search});
                    }
                    return result;
                };
            };
        }]);
});