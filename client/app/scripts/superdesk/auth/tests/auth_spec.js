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

    it('can reload a route after login', inject(function($compile, $rootScope, $route, $q, auth) {
        var elem = $compile('<div sd-login-modal></div>')($rootScope.$new()),
            scope = elem.scope();
        $rootScope.$digest();
        $rootScope.$digest();

        spyOn(auth, 'login').and.returnValue($q.when({}));
        spyOn($route, 'reload');
        $route.current = {};

        scope.authenticate();
        $rootScope.$digest();

        expect($route.reload).not.toHaveBeenCalled();

        $route.current = {redirectTo: '/test'};
        scope.authenticate();
        $rootScope.$digest();

        expect($route.reload).toHaveBeenCalled();
    }));
});
