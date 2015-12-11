(function() {

    'use strict';

    var USER_HREF = 'http://user/1',
        SESSION = 'sess',
        USERNAME = 'foo';

    beforeEach(module('superdesk.preferences'));

    beforeEach(function() {
        module('superdesk.services.storage');
        module('superdesk.auth');
        module('superdesk.session');
        module(function($provide) {
            $provide.service('api', function($q) {
                this.users = {
                    getById: function(id) {
                        return $q.when({username: USERNAME});
                    }
                };
            });
        });
    });

    describe('auth service', function() {
        beforeEach(inject(function(session, preferencesService, $q) {
            session.clear();
            spyOn(preferencesService, 'get').and.returnValue($q.when({}));
        }));

        it('can login', inject(function(auth, session, $httpBackend, $rootScope) {

            expect(session.identity).toBe(null);
            expect(session.token).toBe(null);

            var resolved = {};

            $httpBackend.expectGET(USER_HREF).respond({username: USERNAME});

            session.getIdentity().then(function() {
                resolved.identity = true;
            });

            auth.login('admin', 'admin').then(function(identity) {
                expect(session.identity.username).toBe(USERNAME);
                expect(session.token).toBe(SESSION);
                resolved.login = true;
            });

            $rootScope.$apply();

            expect(resolved.login).toBe(true);
            expect(resolved.identity).toBe(true);
        }));

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
