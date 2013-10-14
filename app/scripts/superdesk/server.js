define([
    'angular',
    'restangular'
], function(angular) {
    'use strict';

    angular.module('superdesk.server', ['restangular'])
        // restanuglar config
        .run(function(Restangular, $http) {
            Restangular.setBaseUrl(ServerConfig.url);
            Restangular.setDefaultHeaders($http.defaults.headers.common);
            Restangular.setRestangularFields({id: '_id'});
            Restangular.setRequestInterceptor(function(element, operation, route, url) {
                switch(operation) {
                    case 'patch':
                    case 'put':
                        // remove extra fields
                        delete element._id;
                        delete element._links;
                        delete element.etag;
                        delete element.updated;
                        delete element.created;
                        // wrap content for eve
                        return {data: element};
                }

                return element;
            });
        })
        .service('server', function($q, Restangular) {
            /**
             * Restangular adapter
             */
            function ServerService() {

                /**
                 * Fetch resource list
                 *
                 * @param {string} resource
                 * @param {Object} parameters
                 * @return {Object} promise
                 */
                this.list = function(resource, parameters) {
                    var delay = $q.defer();

                    Restangular.all(resource)
                    .getList(parameters)
                    .then(function(response) {
                        delay.resolve(response);
                    }, function(response) {
                        delay.reject(response);
                    });

                    return delay.promise;
                };

                /**
                 * Fetch item with given id
                 *
                 * @param {string} resource
                 * @param {string} id
                 * @return {Object} promise
                 */
                this.read = function(resource, id) {
                    return Restangular.one(resource, id).get();
                };

                /**
                 * Update given item
                 *
                 * @param {Object} item
                 * @return {Object} promise
                 */
                this.update = function(item) {
                    var etag = item.etag;
                    var delay = $q.defer();

                    item.patch(item, {}, {
                        'If-Match': etag
                    }).then(function(response) {
                        item._id = response.data._id;
                        item._links = response.data._links;
                        item.etag = response.data.etag;
                        item.updated = response.data.updated;
                        delay.resolve(item);
                    }, function(response) {
                        delay.reject(response);
                    });

                    return delay.promise;
                };

                this._delete = function(resource, id) {
                    var delay = $q.defer();

                    Restangular.one(resource, id).get().then(
                        function(response) {
                            var item = response;
                            item.remove({}, {
                                'If-Match': item.etag
                            }).then(function(response) {
                                delay.resolve(item);
                            }, function(response) {
                                delay.reject(response);
                            });
                        },
                        function(response) {
                            delay.reject(response);
                        }
                    );

                    return delay.promise;
                };

                /**
                 * Delete given item
                 *
                 * @param {string} resource
                 * @param {array} ids
                 * @return {Object} promise
                 */
                this.delete = function(resource, ids) {
                    var self = this;
                    var delay = $q.defer();
                    if (!_.isArray(ids)) {
                        ids = [ids];
                    }
                    
                    var promises = [];
                    _.forEach(ids, function(id) {
                        promises.push(self._delete(resource, id));
                    });
                    
                    $q.all(promises).then(function(response) {
                        delay.resolve(response);
                    });

                    return delay.promise;
                };
            }

            return new ServerService();
        });
});