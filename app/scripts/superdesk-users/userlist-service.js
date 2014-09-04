define([], function() {
    'use strict';

    /**
     * Service for fetching users with caching.
     * Ideally, should be used app-wide.
     */
    UserListService.$inject = ['api', '$q'];
    function UserListService(api, $q) {

        var perPage = 100;
        var cache = {};

        return {
            /**
             * Flushes cached users.
             */
            flushCache: function() {
                cache = {};
            },
            setCache: function(search, page, result) {
                if (!cache[search]) {
                    cache[search] = [];
                }
                if (!cache[search][page]) {
                    cache[search][page] = result;
                }
            },
            /**
             * Fetches and caches users, or returns from the cache.
             *
             * @param {String} search
             * @param {Integer} page (Shouldn't be used at the moment)
             * @returns {Promise}
             */
            get: function(search, page) {
                var self = this;
                page = page || 1;
                var key = search || '_nosearch';

                if (cache[key] && cache[key][page]) {
                    return $q.when(cache[key][page]);
                } else {
                    var criteria = {
                        max_results: perPage
                    };
                    if (search) {
                        criteria.where = JSON.stringify({
                            '$or': [
                                {username: {'$regex': search}},
                                {first_name: {'$regex': search}},
                                {last_name: {'$regex': search}},
                                {display_name: {'$regex': search}},
                                {email: {'$regex': search}}
                            ]
                        });
                    }

                    return api('users').query(criteria)
                    .then(function(result) {
                        self.setCache(key, page, result);
                        return result;
                    });
                }
            }
        };
    }

    return UserListService;
});
