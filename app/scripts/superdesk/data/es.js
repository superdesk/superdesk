define([], function() {
    'use strict';

    /**
     * Elastic search query builder service
     */
    function ElasticSearchQueryService() {

        var SIZE_DEFAULT = 25;

        /**
         * Set from/size for given query and params
         *
         * @param {Object} query
         * @param {Object} params
         * @returns {Object}
         */
        function paginate(query, params) {
            query.size = params.size || SIZE_DEFAULT;
            query.from = (params.page || 0) * query.size;
            return query;
        }

        /**
         * Build query using elastic query dsl
         *
         * @param {Object} params
         * @returns {Object}
         */
        function buildQuery(params) {
            var query = {};

            if (params.q) {
                query = {query_string: {query: params.q}};
            } else {
                query = {match_all: {}};
            }

            if (params.filter) {
                query = {
                    filtered: {
                        query: query,
                        filter: {term: params.filter}
                    }
                };
            }

            return paginate({query: query}, params);
        }

        return buildQuery;
    }

    return ElasticSearchQueryService;
});
