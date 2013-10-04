define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.users.services', []).
        service('converter', function() {
            return new function() {
                this.run = function(params) {
                    var result = {
                        page: params.page,
                        max_results: params.perPage
                    }
                    var sortDirection = 1;
                    if (params.sortDirection === 'desc') {
                        sortDirection = -1;
                    }
                    result.sort = '[("' + params.sortField + '", ' + sortDirection + ')]';
                    if (params.search !== '') {
                        //result.where = '{"display_name": "' + params.search + '"}';
                        result.where = '{"username": "' + params.search + '"}';
                    }
                    return result;
                };
            };
        });
});