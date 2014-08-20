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
            var page = params.page || 1;
            query.size = params.size || SIZE_DEFAULT;
            query.from = (page - 1) * query.size;
            return query;
        }

        /**
         * Build query using elastic query dsl
         *
         * @param {Object} params
         * @param {Array} filters
         * @returns {Object}
         */
        function buildQuery(params, filters) {
            var query = {filtered: {}};

            if (filters && filters.length) {
                query.filtered.filter = {and: filters};
            }

            if (params.q) {
                query.filtered.query = {query_string: {query: params.q}};
            }

            return paginate({query: query}, params);
        }

        return buildQuery;
    }

    return ElasticSearchQueryService;
});
