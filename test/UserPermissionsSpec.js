define([
    'angular',
    'angular-mocks',
    'superdesk/services/entity',
    'superdesk/services/server',
    'superdesk/services/permissionsService'
], function(angular) {
    'use strict';

    describe('PermissionsService', function() {
        var rootScope, httpBackend, em, permissionsService;

        var testPermissions = {
            testResource_1: {read: true},
            testResource_2: {write: true},
            testResource_3: {read: true, write: true}
        };

        beforeEach(function() {
            module('superdesk.services');
            inject(function($rootScope, $httpBackend, _em_, _permissionsService_) {
                rootScope = $rootScope;
                httpBackend = $httpBackend;
                em = _em_;
                permissionsService = _permissionsService_;
            });
        });

        it('can succeed checking role', function() {
            permissionsService.isRoleAllowed(testPermissions, {
                permissions: testPermissions
            }).then(function(result) {
                expect(result).toBe(true);
            });
        });

        it('can fail checking role', function() {
            permissionsService.isRoleAllowed(testPermissions, {
                permissions: {
                    testResource_1: {read: true},
                    testResource_3: {write: true}
                }
            }).then(function(result) {
                expect(result).toBe(false);
            });
        });

        it('can succeed checking user', function() {
            var result = false;

            httpBackend
                .expectGET('http://localhost/user_roles/testRoleId')
                .respond(200, {permissions: testPermissions});

            permissionsService.isUserAllowed(testPermissions, {
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

            permissionsService.isUserAllowed(testPermissions, {
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

            permissionsService.isUserAllowed(testPermissions, false).then(function(isAllowed) {
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

            permissionsService.isUserAllowed(testPermissions, false).then(function(isAllowed) {
                result = isAllowed;
            });

            httpBackend.flush();

            expect(result).toBe(false);
        });

    });
});
