(function() {

'use strict';

function PrivilegesService() {

    this.privileges = {};

    /**
     * Check if current user has given privileges
     *
     * @param {Object} privileges
     */
    this.userHasPrivileges = function userHasPrivileges(privileges) {
        for (var privilege in privileges) {
            if (privileges[privilege] && !this.privileges[privilege]) {
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
                this.privileges[privilege] = 1;
            } else {
                this.privileges[privilege] = 0;
            }
        }
    };
}

angular.module('superdesk.privileges', [])
    .service('privileges', PrivilegesService);

})();
