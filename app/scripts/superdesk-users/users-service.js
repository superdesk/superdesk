define(['lodash', 'superdesk/hashlib'], function(_, hashlib) {
    'use strict';

    /**
     * Bussiness logic layer, should be used instead of resource
     */
    APIService.$inject = ['resource'];
    function APIService(resource) {

        // todo(petr): generate via api provider
        this.users = {

            /**
             * Save user with given data
             *
             * @param {Object} user
             * @param {Object} data
             * @returns {Promise}
             */
            save: function(user, data) {
                _.defaults(data, user);

                if (data.Password) {
                    data.Password = hashlib.hash(data.Password);
                }

                return resource.users.save(data)
                    .then(function(updates) {
                        _.extend(user, updates);
                        _.extend(data, user);
                        return user;
                    });
            }
        };
    }

    return APIService;
});
