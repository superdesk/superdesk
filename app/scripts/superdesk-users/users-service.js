define(['angular'], function(angular) {
    'use strict';

    /**
     * Bussiness logic layer, should be used instead of resource
     */
    UsersService.$inject = ['resource', '$q'];
    function UsersService(resource, $q) {

        /**
         * Save user with given data
         *
         * @param {Object} user
         * @param {Object} data
         * @returns {Promise}
         */
        this.save = function(user, data) {
            var copy = _.clone(data);
            return resource.save(user, copy)
                .then(function(updates) {
                    angular.extend(user, data);
                    angular.extend(user, updates);
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
            console.error('change password not implemented');
            return $q.reject();
        };
    }

    return UsersService;
});
