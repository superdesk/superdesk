define(['superdesk/auth/session-service'], function(SessionService) {
    'use strict';

    describe('session service', function() {

        beforeEach(function() {
            localStorage.clear();
            module(function($provide) {
                $provide.service('session', SessionService);
            });
        });

        it('has identity and token property', inject(function(session) {
            expect(session.token).toBe(null);
            expect(session.identity).toBe(null);
        }));

        it('can be started', inject(function(session) {
            session.start('token', {name: 'user'});
            expect(session.token).toBe('token');
            expect(session.identity.name).toBe('user');
        }));

        it('can be set expired', inject(function(session) {
            session.start('token', {name: 'foo'});
            session.expire();
            expect(session.token).toBe(null);
            expect(session.identity.name).toBe('foo');
        }));

        it('can resolve identity on start', inject(function(session, $rootScope) {
            var resolved = false;

            session.getIdentity().then(function(identity) {
                expect(identity.name).toBe('foo');
                resolved = true;
            });

            session.start('test', {name: 'foo'});

            $rootScope.$apply();
            expect(resolved).toBe(true);
        }));

        it('can store state for future requests', inject(function(session, $injector) {
            session.start('token', {name: 'bar'});

            var nextSession = $injector.instantiate(SessionService);
            expect(nextSession.token).toBe('token');
            expect(nextSession.identity.name).toBe('bar');

            nextSession.expire();

            nextSession = $injector.instantiate(SessionService);
            expect(nextSession.token).toBe(null);
            expect(nextSession.identity.name).toBe('bar');
        }));

        it('can clear session', inject(function(session) {
            session.start('token', {name: 'bar'});
            session.clear();
            expect(session.token).toBe(null);
            expect(session.identity).toBe(null);
        }));
    });
});
