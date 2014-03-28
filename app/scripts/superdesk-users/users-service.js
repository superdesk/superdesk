define(['lodash', 'superdesk/hashlib'], function(_, hashlib) {
    'use strict';

    /**
     * Bussiness logic layer, should be used instead of resource
     */
    UsersService.$inject = ['resource'];
    function UsersService(resource) {

        /**
         * Save user with given data
         *
         * @param {Object} user
         * @param {Object} data
         * @returns {Promise}
         */
        this.save = function(user, data) {
            _.defaults(data, user);

            var newData = _.extend({}, data);

            if (newData.Password) {
                newData.Password = hashlib.hash(newData.Password);
            }

            return resource.save(newData)
                .then(function(updates) {
                    _.extend(user, updates);
                    _.extend(data, user);
                    return user;
                });
        };

        /**
         * Change user password
         *
         * @param {Object} user
         * @param {string} oldPassword
         * @param {string} newPassword
         * @returns {Promise}
         */
        this.changePassword = function(user, oldPassword, newPassword) {
            return resource.replace(user.UserPassword.href, {
                OldPassword: hashlib.hash(oldPassword),
                NewPassword: hashlib.hash(newPassword)
            });
        };
    }

    return UsersService;
});
