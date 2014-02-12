/* jshint maxlen:false */
define([
    'superdesk/auth/auth',
    'angular-mocks'
], function() {
    'use strict';

    // taken from server examples
    var TOKEN_URL = '/Security/Authentication',
        LOGIN_URL = '/Security/Login',
        username = 'admin',
        password = 'a',
        token = '07e4f625f5e8f5e380b181a5f8816dfb75418dcbe1c9da4d225895ae37bcaf20507c15e0f78f183e25debe30ba81df1e09e379b493aec02dc194fde73e9fc71e',
        hashedToken = 'bc6adf5c3d7367a4ae4ce3ef6abe6024cd327f5d3ddaadff400d146126a16f96e4ae763a1bf1a858dad4701fecc35f73785cc397ac54487d30da3313a0d7e5f4',
        session = 'xyz';

    beforeEach(function() {
        module('superdesk.auth');
    });

    describe('server authentication', function() {
        it('can login', inject(function(auth, $httpBackend) {
            $httpBackend.expectPOST(TOKEN_URL).respond({Token: token});
            $httpBackend.expectPOST(LOGIN_URL, {UserName: username, Token: token, HashedToken: hashedToken}).respond({Session: session});

            auth.login(username, password).then(function(sessionData) {
                expect(sessionData.Session).toBe(session);
            });

            $httpBackend.flush();
        }));
    });
});
