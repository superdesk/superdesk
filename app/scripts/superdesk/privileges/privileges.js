(function() {

'use strict';

PrivilegesService.$inject = ['$rootScope', '$q', 'preferencesService'];
function PrivilegesService($rootScope, $q, preferencesService) {
    var _privileges = {};
    this.privileges = _privileges;
    $rootScope.privileges = _privileges;

    /**
     * Check if current user has given privileges
     *
     * @param {Object} privileges
     */
    this.userHasPrivileges = function userHasPrivileges(privileges) {
        for (var privilege in privileges) {
            if (privileges[privilege] && !_privileges[privilege]) {
                return false;
            }
        }

        return true;
    };

    /**
     * Set current user privileges
     *
     * @param {Object} privileges
     */
    this.setUserPrivileges = function setUserPrivileges(privileges) {
        for (var privilege in privileges) {
            if (privileges[privilege]) {
                _privileges[privilege] = 1;
            } else {
                _privileges[privilege] = 0;
            }
        }

        return _privileges;
    };

    /**
     * Load user privileges
     */
    this.load = function load() {
        return preferencesService.getPrivileges().then(this.setUserPrivileges);
    };
}

angular.module('superdesk.privileges', ['superdesk.preferences'])
    .service('privileges', PrivilegesService);

})();
