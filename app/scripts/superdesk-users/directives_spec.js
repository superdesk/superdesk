define([
    'superdesk/data/resource-provider',
    'superdesk-users/directives',
    'angular-mocks'
], function(resourceProvider) {
    'use strict';

    describe('sdUserUnique Directive', function() {
        var $compile, $rootScope, httpBackend;

        beforeEach(module('superdesk.users.directives'));
        beforeEach(module('ngMock'));

        beforeEach(inject(function($injector) {
            $compile = $injector.get('$compile');
            $rootScope = $injector.get('$rootScope');
            httpBackend = $injector.get('$httpBackend');
        }));

        it('succeeds validating unique user by userName', function() {
            
            var elem = $compile('<form name="userForm"><input sd-user-unique data-unique-field="userName" value="testUsername"></form>')($rootScope);
            
            /*
            httpBackend
                .expectGET('http://HR/User/?userName=testUsername')
                .respond(200, {
                    total:1,
                    maxResults:30,
                    offset:0,
                    collection:[{
                        href:'https://apytest.apy.sd-test.sourcefabric.org/api/HR/User/1',
                        Id:1,
                        Active:true,
                        EMail:'User.Admin@email.addr',
                        FirstName:'User',
                        FullName:'User Admin',
                        LastName:'Admin',
                        UserName:'admin',
                        CreatedOn:'2014-03-17T11:47:36Z',
                        Avatar:{href:'http://www.gravatar.com/avatar/a3959a77482a11a08385adc04d04199c?s=200'},
                        ActionList:{href:'https://apytest.apy.sd-test.sourcefabric.org/api/HR/User/1/Action/'},
                        AllActionList:{href:'https://apytest.apy.sd-test.sourcefabric.org/api/HR/User/1/AllAction/'},
                        RightList:{href:'https://apytest.apy.sd-test.sourcefabric.org/api/HR/User/1/Right/'},
                        RoleList:{href:'https://apytest.apy.sd-test.sourcefabric.org/api/HR/User/1/Role/'}
                    }]
                });
            */

            $rootScope.$digest();

            httpBackend.flush();
        });

        it('fails validating unique user by userName', function() {
            
        });

        it('succeeds validating unique user by EMail', function() {
            
        });

        it('fails validating unique user by EMail', function() {
            
        });
    });
});
