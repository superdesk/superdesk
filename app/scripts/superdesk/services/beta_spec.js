define(['superdesk/services/beta'], function(BetaService) {
    'use strict';

    describe('beta service', function() {

        beforeEach(module(BetaService.name));

        it('can filter out sd-beta from html when beta is off', inject(function(betaService, $rootScope, $http, $httpBackend) {
            $rootScope.beta = false;
            expect(betaService.isBeta()).toBe(false);

            var template = '<div>normal</div><div sd-beta>beta</div>',
                data;

            $httpBackend.expectGET('view_off.html').respond(200, template);

            $http.get('view_off.html').then(function(response) {
                data = response.data;
            });

            $httpBackend.flush();

            expect(data).not.toContain('beta');
        }));

        it('keeps it there when beta is on', inject(function(betaService, $rootScope, $http, $httpBackend) {
            $rootScope.beta = true;
            expect(betaService.isBeta()).toBe(true);

            var template = '<div sd-beta>beta</div>',
                data;

            $httpBackend.expectGET('view_on.html').respond(200, template);

            $http.get('view_on.html').then(function(response) {
                data = response.data;
            });

            $httpBackend.flush();

            expect(data).toContain('beta');
        }));
    });
});
