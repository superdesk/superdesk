define([], function() {
    'use strict';

    SuperdeskAuthAdapter.$inject = ['$http', '$q', 'config'];
    function SuperdeskAuthAdapter($http, $q, config) {

        /**
         * Authenticate using given credentials
         *
         * @param {string} username
         * @param {string} password
         * @returns {object} promise
         */
        this.authenticate = function(username, password) {
            return $http.post(config.server.url + '/auth', {
                username: username,
                password: password
            }).then(function(response) {
                response.data.token = 'Basic ' + btoa(response.data.token + ':');
                $http.defaults.headers.common.Authorization = response.data.token;
                return response.data;
            });
        };
    }

    return SuperdeskAuthAdapter;
});
