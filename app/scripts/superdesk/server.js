define([
    'angular',
    'restangular'
], function(angular) {
    'use strict';

    var ResourceBase = function() {
        this.links = {};
    };
    ResourceBase.prototype.setLinks = function(links) {
        for (var i in links) {
            if (links[i] !== null && links[i].href !== undefined) {
                this.links[i] = links[i].href;
            }
        }
    };

    var ResourceList = function(response) {
        ResourceBase.call(this);

        this.items = [];

        if (response !== undefined) {
            this.items = response._items;

            for (var i = 0; i < response._items.length; i++) {
                this.items[i] = new ResourceItem(response._items[i]);
            }

            this.setLinks(response._links);
        }
    };
    ResourceList.prototype = new ResourceBase();
    ResourceList.prototype.constructor = ResourceList;

    var ResourceItem = function(response) {
        ResourceBase.call(this);

        if (response !== undefined) {
            for (var i in response) {
                if (i !== '_links') {
                    this[i] = response[i];
                }
            }
            
            this.setLinks(response._links);
        }
    };
    ResourceItem.prototype = new ResourceBase();
    ResourceItem.prototype.constructor = ResourceItem;

    //

    angular.module('superdesk.server', ['restangular'])
        // restanuglar config
        .run(function(Restangular, $http) {
            Restangular.setBaseUrl(ServerConfig.url);
            Restangular.setDefaultHeaders($http.defaults.headers.common);
            Restangular.setRestangularFields({id: '_id'});
            Restangular.setRequestInterceptor(function(element, operation) {
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
                this.readList = function(resource, parameters) {
                    var delay = $q.defer();

                    Restangular.all(resource)
                    .getList(parameters)
                    .then(function(response) {
                        var resourceList = new ResourceList(response);
                        delay.resolve(resourceList);
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
                this.readItem = function(resource, id) {
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
            }

            return new ServerService();
        });
});