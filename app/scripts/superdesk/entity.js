define(['angular', 'lodash', './server'], function(angular, _) {
    'use strict';

    angular.module('superdesk.entity', ['superdesk.server'])
        .factory('Criteria', function() {
            function Criteria(defaultParams, currentParams) {
                _.extend(defaultParams, {page: 1});
                _.assign(this, defaultParams);
                _.assign(this, currentParams);

                this.set = function(key, val) {
                    this[key] = val;
                    return (key in defaultParams && defaultParams[key] === val) ? null : val;
                };
            }

            return Criteria;
        })
        .factory('Repository', function(server) {
            return function(entity) {
                this.matching = function(criteria) {
                    var criteriaValObj = _.omit(criteria, _.functions(criteria));
                    var promise = server.list(entity, criteriaValObj);
                    promise.then(function(result) {
                        result._criteria = criteria;
                    });

                    return promise;
                };
            };
        })
        .service('em', function(Repository) {
            return {
                getRepository: function(entity) {
                    return new Repository(entity);
                }
            };
        });
});