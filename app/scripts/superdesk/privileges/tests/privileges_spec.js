'use strict';

describe('privileges', function() {

    beforeEach(module('superdesk.api'));
    beforeEach(module('superdesk.privileges'));

    beforeEach(inject(function(preferencesService, api, $q) {
        spyOn(preferencesService, 'getPrivileges').and.returnValue($q.when({tests: 1}));
        spyOn(api, 'find').and.returnValue($q.reject()); // stop preferences processing
    }));

    it('can expose user privileges on $rootScope', inject(function(privileges, $rootScope) {
        expect($rootScope.$eval('!!privileges.tests')).toBe(false);
        privileges.setUserPrivileges({tests: 1});
        $rootScope.$digest();
        expect($rootScope.$eval('!!privileges.tests')).toBe(true);
    }));

    it('reads privileges via preferences', inject(function(privileges, $rootScope) {
        $rootScope.$digest();
        expect(privileges.privileges.tests).toBe(1);
    }));
});
