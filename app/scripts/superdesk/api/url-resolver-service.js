define([], function() {
    'use strict';

    function URLResolver($http, $q, config) {
        var links;

        this.get = function(title) {
            return getResourceLinks().then(function() {
                return links[title] ? links[title] : $q.reject(title);
            });
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
                        links[link.title] = 'http://' + link.href;
                    });
                }

                return links;
            });
        }
    }

    return URLResolver;
});
