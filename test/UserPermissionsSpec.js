define([
    'angular',
    'superdesk/entity',
    'superdesk/services/userPermissions',
    'angular-mocks'
], function(angular) {
    'use strict';

    describe('UserPermissions', function() {
        var rootScope, httpBackend, em, userPermissions;

        var testPermissions = {
            testResource_1: {read: true},
            testResource_2: {write: true,},
            testResource_3: {read: true, write: true}
        };

        beforeEach(function() {
            module('superdesk.entity');
            module('superdesk.services.userPermissions');
            inject(function($rootScope, $httpBackend, _em_, _userPermissions_) {
                rootScope = $rootScope;
                httpBackend = $httpBackend;
                em = _em_;
                userPermissions = _userPermissions_;
            });
        });

        it('can succeed checking role', function() {
            var result = userPermissions.isRoleAllowed(testPermissions, {
                permissions: testPermissions
            });

            expect(result).toBe(true);
        });

        it('can fail checking role', function() {
            var result = userPermissions.isRoleAllowed(testPermissions, {
                permissions: {
                    testResource_1: {read: true},
                    testResource_3: {write: true}
                }
            });

            expect(result).toBe(false);
        });

        it('can succeed checking user', function() {
            var result = false;

            httpBackend
                .expectGET('http://localhost/user_roles/testRoleId')
                .respond(200, {permissions: testPermissions});

            userPermissions.isUserAllowed(testPermissions, {
                role: 'testRoleId'
            }).then(function(isAllowed) {
                result = isAllowed;
            });

            httpBackend.flush();
            
            expect(result).toBe(true);
        });

        it('can fail checking user', function() {
            var result = false;

            httpBackend
                .expectGET('http://localhost/user_roles/testRoleId')
                .respond(200, {permissions: {testResource_1: {read: true}}});

            userPermissions.isUserAllowed(testPermissions, {
                role: 'testRoleId'
            }).then(function(isAllowed) {
                result = isAllowed;
            });

            httpBackend.flush();
            
            expect(result).toBe(false);
        });

        it('can succeed checking current user', function() {
            var result = false;

            rootScope.currentUser = {role: 'testRoleId'};

            httpBackend
                .expectGET('http://localhost/user_roles/testRoleId')
                .respond(200, {permissions: testPermissions});

            userPermissions.isUserAllowed(testPermissions, false).then(function(isAllowed) {
                result = isAllowed;
            });

            httpBackend.flush();
            
            expect(result).toBe(true);
        });

        it('can fail checking current user', function() {
            var result = false;

            rootScope.currentUser = {role: 'testRoleId'};

            httpBackend
                .expectGET('http://localhost/user_roles/testRoleId')
                .respond(200, {permissions: {testResource_1: {read: true}}});

            userPermissions.isUserAllowed(testPermissions, false).then(function(isAllowed) {
                result = isAllowed;
            });

            httpBackend.flush();
            
            expect(result).toBe(false);
        });

    });
});
