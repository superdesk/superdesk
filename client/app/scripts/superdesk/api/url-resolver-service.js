define([], function() {
    'use strict';

    URLResolver.$inject = ['$http', '$q', 'config'];
    function URLResolver($http, $q, config) {

        var _links, baseUrl = config.server.url;

        function basejoin(path) {
            return baseUrl + (path.indexOf('/') === 0 ? path : ('/' + path));
        }

        /**
         * Get url for given resource
         *
         * @param {String} resource
         * @returns Promise
         */
        this.resource = function(resource) {
            return this.links().then(function() {
                return _links[resource] ? _links[resource] : $q.reject({status: 404, resource: resource});
            });
        };

        /**
         * Get server url for given item
         *
         * @param {String} item
         * @returns {String}
         */
        this.item = function(item) {
            return basejoin(item);
        };

        /**
         * Get resource links
         */
        this.links = function() {
            if (_links) {
                return $q.when(_links);
            }

            return fetchResourceLinks();
        };

        /**
         * Fetch resource links via root url
         *
         * @returns {Promise}
         */
        function fetchResourceLinks() {
            if (!baseUrl) {
                return $q.reject();
            }

            return $http({
                method: 'GET',
                url: baseUrl,
                cache: true
            }).then(function(response) {
                _links = {};

                if (response.status === 200) {
                    _.each(response.data._links.child, function(link) {
                        _links[link.title] = basejoin(link.href);
                    });
                } else {
                    $q.reject(response);
                }

                return _links;
            });
        }
    }

    return URLResolver;
});
