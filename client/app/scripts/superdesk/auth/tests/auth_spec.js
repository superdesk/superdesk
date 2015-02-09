'use strict';

describe('auth', function() {

    beforeEach(module('templates'));
    beforeEach(module('superdesk.activity'));
    beforeEach(module('superdesk.auth'));

    it('can use routes with auth=false without identity', inject(function($rootScope, $location, $route) {
        $location.path('/reset-password/');
        $rootScope.$digest();
        expect($location.path()).toBe('/reset-password/');
    }));
});
