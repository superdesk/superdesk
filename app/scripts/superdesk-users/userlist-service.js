define([], function() {
    'use strict';

    /**
     * Service for fetching users with caching.
     * Ideally, should be used app-wide.
     */
    UserListService.$inject = ['api', '$q', '$cacheFactory'];
    function UserListService(api, $q, $cacheFactory) {

        var perPage = 100;
        var cache = $cacheFactory('userList');

        return {
            /**
             * Fetches and caches users, or returns from the cache.
             *
             * @param {String} search
             * @param {Integer} page (Shouldn't be used at the moment)
             * @returns {Promise}
             */
            get: function(search, page) {
                page = page || 1;
                var key = search || '_nosearch';
                key = key + '_' + page;

                var value = cache.get(key);
                if (value) {
                    return $q.when(value);
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
                        cache.put(key, result);
                        return result;
                    });
                }
            }
        };
    }

    return UserListService;
});
