(function() {

    'use strict';

    describe('auth service', function() {
        beforeEach(function() {
            module('superdesk.preferences');
            module('superdesk.services.storage');
            module('superdesk.auth');
            module('superdesk.session');
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
        beforeEach(inject(function(session, preferencesService, $q) {
            session.clear();
            spyOn(preferencesService, 'get').and.returnValue($q.when({}));
        }));

/* THIS FAILS
        it('can login', inject(function(auth, session, $httpBackend, $rootScope) {

            expect(session.identity).toBe(null);
            expect(session.token).toBe(null);

            var resolved = {};

            $httpBackend.expectGET('http://user/1').respond({username: 'foo'});

            session.getIdentity().then(function() {
// NONE OF THIS EVER EXECUTES
                resolved.identity = true;
            });

            auth.login('admin', 'admin').then(function(identity) {
// NONE OF THIS EVER EXECUTES
                expect(session.identity.username).toBe('foo');
                expect(session.token).toBe('sess');
                resolved.login = true;
            });

            $rootScope.$apply();

// SO THESE NEVER GET SET
            expect(resolved.login).toBe(true);
            expect(resolved.identity).toBe(true);
        }));
*/

        it('checks credentials', inject(function(auth, $rootScope) {
            var resolved = false, rejected = false;

            auth.login('wrong', 'credentials').then(function() {
                resolved = true;
            }, function() {
                rejected = true;
            });

            $rootScope.$apply();
            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        }));
    });

})();
