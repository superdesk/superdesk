define([], function() {
    'use strict';

    URLResolver.$inject = ['$http', '$q', 'config'];
    function URLResolver($http, $q, config) {

        var links;

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
            return item; // noop - items should have full urls now
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
                url: config.server.url
            }).then(function(response) {
                links = {};

                if (response.status === 200) {
                    _.each(response.data._links.child, function(link) {
                        links[link.title] = link.href;
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
