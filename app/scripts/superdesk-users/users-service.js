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

                var newData = _.extend({}, data);

                if (newData.Password) {
                    newData.Password = hashlib.hash(newData.Password);
                }

                return resource.users.save(newData)
                    .then(function(updates) {
                        _.extend(user, updates);
                        _.extend(data, user);
                        return user;
                    });
            },

            /**
             * Change user password
             *
             * @param {Object} user
             * @param {string} oldPassword
             * @param {string} newPassword
             * @returns {Promise}
             */
            changePassword: function(user, oldPassword, newPassword) {
                return resource.users.replace(user.UserPassword.href, {
                    OldPassword: hashlib.hash(oldPassword),
                    NewPassword: hashlib.hash(newPassword)
                });
            }
        };
    }

    return APIService;
});
