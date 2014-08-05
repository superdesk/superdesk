define([], function() {
    'use strict';

    URLResolver.$inject = ['$http', '$q', 'config'];
    function URLResolver($http, $q, config) {

        var links, baseUrl = config.server.url;

        function basejoin(path) {
            return baseUrl + path;
        }

        /**
         * Get url for given resource
         *
         * @param {String} resource
         * @returns Promise
         */
        this.resource = function(resource) {
            return getResourceLinks().then(function() {
                return links[resource] ? links[resource] : $q.reject(resource);
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
         * Get resource links via root url
         *
         * @returns {Promise}
         */
        function getResourceLinks() {
            if (links != null) {
                return $q.when(links);
            }

            return $http({
                method: 'GET',
                url: baseUrl
            }).then(function(response) {
                links = {};

                if (response.status === 200) {
                    _.each(response.data._links.child, function(link) {
                        links[link.title] = basejoin(link.href);
                    });
                } else {
                    $q.reject(response);
                }

                return links;
            });
        }
    }

    return URLResolver;
});
