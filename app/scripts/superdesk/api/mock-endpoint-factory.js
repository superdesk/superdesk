define(['lodash'], function(_) {
    'use strict';

    /**
     * Mock endpoint
     */
    MockEndpointFactory.$inject = ['$q'];
    function MockEndpointFactory($q) {

        function MockCursor(data) {
            this.total = data.length;
            this._items = data;
            this.collection = data;
        }

        /**
         * Mock API endpoint
         */
        function MockEndpoint(name, config) {
            this.name = name;
            this.data = _.create(config.data);
            this.url = config.url || null;
        }

        /**
         * Select items matching given criteria
         *
         * @param {Object} criteria
         * @returns {Promise}
         */
        MockEndpoint.prototype.query = function(criteria) {
            var matches = _.filter(this.data, criteria);
            return $q.when(new MockCursor(matches));
        };

        /**
         * Find item by given id
         *
         * @param {string} id
         * @returns {Promise}
         */
        MockEndpoint.prototype.find = function(id) {
            var item = _.find(this.data, {Id: id});
            return item ? $q.when(item) : $q.reject(item);
        };

        /**
         * Save item
         *
         * @param {Object} item
         * @param {Object} diff
         * @returns {Promise}
         */
        MockEndpoint.prototype.save = function(item, diff) {

            _.extend(item, diff);

            if (!item.Id) {
                item.Id = _.max(_.pluck(this.data, 'Id')) + 1;
                this.data.push(item);
            }

            return $q.when(item);
        };

        /**
         * Remove an item
         *
         * @param {Object} item
         * @returns {Promise}
         */
        MockEndpoint.prototype.remove = function(item) {
            _.remove(this.data, item);
            return $q.when(item);
        };

        /**
         * Get url - there is no url, it is here to match http api endpoint
         *
         * @returns {Promise}
         */
        MockEndpoint.prototype.getUrl = function() {
            return $q.when(this.url);
        };

        return MockEndpoint;
    }

    return MockEndpointFactory;
});
