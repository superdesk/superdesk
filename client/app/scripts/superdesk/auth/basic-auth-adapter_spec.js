(function() {
    'use strict';

    /* jshint maxlen:false */
    var SERVER_URL = 'http://localhost/resource',
        LOGIN_URL = SERVER_URL + '/auth',
        username = 'admin',
        password = 'admin',
        session = 'xyz';

    describe('basic auth adapter', function() {
        var $httpBackend;

        beforeEach(module('superdesk.auth'));
        beforeEach(module('superdesk.menu'));
        beforeEach(module('superdesk.authoring'));
        beforeEach(inject(function (_$httpBackend_) {
            $httpBackend = _$httpBackend_;
        }));

        afterEach(function() {
            $httpBackend.verifyNoOutstandingExpectation();
            $httpBackend.verifyNoOutstandingRequest();
        });

        it('can login', inject(function(authAdapter, urls, $q) {
            $httpBackend
                .expectPOST(LOGIN_URL, {username: username, password: password})
                    .respond({token: session, user: '1'});

            spyOn(urls, 'resource').and.returnValue($q.when(LOGIN_URL));

            var identity;
            authAdapter.authenticate(username, password).then(function(_identity) {
                identity = _identity;
            });

            $httpBackend.flush();

            expect(urls.resource).toHaveBeenCalledWith('auth');
            expect(identity.token).toBe('Basic ' + btoa(session + ':'));
        }));

        it('can reject on failed auth', inject(function(authAdapter, urls, $q) {
            var resolved = false, rejected = false;

            spyOn(urls, 'resource').and.returnValue($q.when(LOGIN_URL));

            $httpBackend.expectPOST(LOGIN_URL).respond(400);

            authAdapter.authenticate(username, password)
                .then(function() {
                    resolved = true;
                }, function() {
                    rejected = true;
                });

            $httpBackend.flush();

            expect(resolved).toBe(false);
            expect(rejected).toBe(true);
        }));

    });
})();
