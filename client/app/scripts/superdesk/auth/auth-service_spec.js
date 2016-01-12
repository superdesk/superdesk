(function() {

    'use strict';

    describe('auth service', function() {
        beforeEach(function() {
            module('superdesk.preferences');
            module('superdesk.services.storage');
            module('superdesk.auth');
            module('superdesk.session');
            module('superdesk.menu');
            module('superdesk.authoring');
            module(function($provide) {
                $provide.service('api', function($q) {
                    this.users = {
                        getById: function(id) {
                            return $q.when({username: 'foo'});
                        }
                    };
                });
            });
        });
        beforeEach(inject(function(session, preferencesService, authAdapter, urls, $q) {
            session.clear();
            spyOn(preferencesService, 'get').and.returnValue($q.when({}));
            spyOn(urls, 'resource').and.returnValue($q.when('http://localhost:5000/api/auth'));
            spyOn(session, 'start').and.returnValue(true);
        }));

        it('can login', inject(function(auth, session, $httpBackend, $rootScope) {

            expect(session.identity).toBe(null);
            expect(session.token).toBe(null);

            var resolved = {};

            $httpBackend.expectPOST('http://localhost:5000/api/auth').respond(200, {
                user: 'foo'
            });

            auth.login('admin', 'admin').then(function(identity) {
                expect(session.start).toHaveBeenCalled();
                resolved.login = true;
            }, function() {
                resolved.login = false;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(resolved.login).toBe(true);
        }));

        it('checks credentials', inject(function(auth, $httpBackend, $rootScope) {
            var resolved = false, rejected = false;

            $httpBackend.expectPOST('http://localhost:5000/api/auth').respond(403, {});

            auth.login('wrong', 'credentials').then(function() {
                resolved = true;
            }, function() {
                rejected = true;
            });

            $httpBackend.flush();
            $rootScope.$apply();

            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        }));
    });

})();
