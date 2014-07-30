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
            var copy = _.clone(data);

            if (copy.Password) {
                copy.Password = hashlib.hash(copy.Password);
            }

            return resource.save(user, copy)
                .then(function(updates) {
                    _.extend(user, data);
                    _.extend(user, updates);
                    delete user.Password;
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
