'use strict';

describe('privileges', function() {

    beforeEach(module('superdesk.privileges'));

    it('can expose user privileges on $rootScope', inject(function(privileges, $rootScope) {
        expect($rootScope.$eval('!!privileges.tests')).toBe(false);
        privileges.setUserPrivileges({tests: 1});
        $rootScope.$digest();
        expect($rootScope.$eval('!!privileges.tests')).toBe(true);
    }));
});
