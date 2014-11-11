define([
    'angular',
    './http-endpoint-factory'
], function(angular, HttpEndpointFactory) {
    'use strict';

    /**
     * Api layer provider
     */
    function APIProvider() {
        var apis = {};

        /**
         * Register an api
         */
        this.api = function(name, config) {
            apis[name] = config;
            return this;
        };

        this.$get = apiServiceFactory;

        apiServiceFactory.$inject = ['$injector', '$q', '$http', 'urls'];
        function apiServiceFactory($injector, $q, $http, urls) {

            var endpoints = {
                'http': $injector.invoke(HttpEndpointFactory)
            };

            function isOK(response) {

                function isErrData(data) {
                    return data && data._status && data._status === 'ERR';
                }

                return response.status >= 200 && response.status < 300 && !isErrData(response.data);
            }

            /**
             * Call $http once url is resolved
             */
            function http(config) {
                return $q.when(config.url).then(function(url) {
                    config.url = url;
                    return $http(config);
                }).then(function(response) {
                    return isOK(response) ? response.data : $q.reject(response);
                });
            }

            /**
             * Remove keys prefixed with '_'
             */
            function clean(data, keepId) {
                var fields = ['_updated', '_created', '_etag', '_links'];
                if (!keepId) {
                    fields.push('_id');
                }
                return _.omit(data, fields);
            }

            /**
             * Get headers for given item
             */
            function getHeaders(item) {
                var headers = {};

                if (item && item._etag) {
                    headers['If-Match'] = item._etag;
                }

                return headers;
            }

            /**
             * API Resource instance
             */
            function Resource(resource, parent) {
                this.resource = resource;
                this.parent = parent;
            }

            /**
             * Get resource url
             */
            Resource.prototype.url = function(_id) {

                function resolve(urlTemplate, data) {
                    return urlTemplate.replace(/<.*>/, data._id);
                }

                return urls.resource(this.resource)
                    .then(angular.bind(this, function(url) {
                        if (this.parent) {
                            url = resolve(url, this.parent);
                        }

                        if (_id) {
                            url = url + '/' + _id;
                        }

                        return url;
                    }));
            };

            /**
             * Save an item
             */
            Resource.prototype.save = function(item, diff, params) {
                return http({
                    method: item._links ? 'PATCH' : 'POST',
                    url: item._links ? urls.item(item._links.self.href) : this.url(),
                    data: diff ? diff : clean(item, !!!item._links),
                    params: params,
                    headers: getHeaders(item)
                }).then(function(data) {
                    angular.extend(item, diff || {});
                    angular.extend(item, data);
                    return item;
                });
            };

            /**
             * Replace an item
             */
            Resource.prototype.replace = function(item) {
                return http({
                    method: 'PUT',
                    url: this.url(item._id),
                    data: clean(item)
                });
            };

            /**
             * Query resource
             */
            Resource.prototype.query = function(params) {
                return http({
                    method: 'GET',
                    url: this.url(),
                    params: params
                });
            };

            /**
             * Get an item by _id
             *
             * @param {String} _id
             */
            Resource.prototype.getById = function(_id, params) {
                return http({
                    method: 'GET',
                    url: this.url(_id),
                    params: params
                });
            };

            /**
             * Remove an item
             *
             * @param {Object} item
             */
            Resource.prototype.remove = function(item, params) {
                return http({
                    method: 'DELETE',
                    url: urls.item(item._links.self.href),
                    params: params,
                    headers: getHeaders(item)
                });
            };

            // api service
            var api = function apiService(resource, parent) {
                return new Resource(resource, parent);
            };

            /**
             * @alias api(resource).getById(id)
             */
            api.find = function apiFind(resource, id, params) {
                return api(resource).getById(id, params);
            };

            /**
             * @alias api(resource).save(dest, diff)
             */
            api.save = function apiSave(resource, dest, diff, parent) {
                return api(resource, parent).save(dest, diff);
            };

            /**
             * Remove a given item.
             */
            api.remove = function apiRemove(item, params, resource) {
                var url = resource ? getResourceUrl(resource, item) : urls.item(item._links.self.href);
                return http({
                    method: 'DELETE',
                    url: url,
                    params: params,
                    headers: getHeaders(item)
                });
            };

            /**
             * Query qiven resource
             *
             * @param {string} resource
             * @param {Object} query
             */
            api.query = function apiQuery(resource, query) {
                return api(resource).query(query);
            };

            function getResourceUrl(resource, item) {
                return api(resource, item).url();
            }

            /**
             * Get on a given url
             *
             * @param {string} url
             */
            api.get = function apiGet(url, params) {
                return http({
                    method: 'GET',
                    url: urls.item(url),
                    params: params
                });
            };

            angular.forEach(apis, function(config, apiName) {
                var service = config.service || _.noop;
                service.prototype = new endpoints[config.type](apiName, config.backend);
                api[apiName] = $injector.instantiate(service, {resource: service.prototype});
            });

            return api;
        }
    }

    return APIProvider;
});
