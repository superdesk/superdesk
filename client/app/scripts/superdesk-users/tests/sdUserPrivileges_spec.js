
/**
* Module with tests for the sdUserPrivileges directive
*
* @module sdUserPrivileges directive tests
*/
describe('sdUserPrivileges directive', function() {
    'use strict';

    var queryDeferred,
        getByIdDeferred,
        fakeEndpoints,
        isoScope,  // the directive's own isolate scope
        $compile,
        $rootScope;

    beforeEach(module('superdesk.templates-cache'));
    beforeEach(module('superdesk.users'));

    beforeEach(module(function ($provide) {
        fakeEndpoints = {};

        function fakeApi() {
            function apiMock(endpointName) {
                return fakeEndpoints[endpointName];
            }

            // some API methods are attached directly to the API service, thus
            // a different mocking technique here
            apiMock.save = jasmine.createSpy('api_save');

            return apiMock;
        }

        $provide.service('api', fakeApi);
    }));

    beforeEach(inject(function (_$rootScope_, _$compile_, $q, api) {
        $rootScope = _$rootScope_;
        $compile = _$compile_;

        queryDeferred = $q.defer();
        getByIdDeferred = $q.defer();

        fakeEndpoints.privileges = {
            query: jasmine.createSpy('privileges_query')
                        .and.returnValue(queryDeferred.promise)
        };

        fakeEndpoints.roles = {
            getById: jasmine.createSpy('get_roles_by_user_id')
                        .and.returnValue(getByIdDeferred.promise)
        };
    }));

    /**
     * Compiles the directive under test and links it with a new scope
     * containing the provided scope values.
     * Provided values should contain at least a "user" object, since the
     * directive undertest expects it to be present in the parent scope.
     *
     * @function compileDirective
     * @param {Object} scopeValues - values in the current scope of the DOM
     *   element the directive will be applied to
     * @return {Object} - the root DOM node of the compiled directive
     *   element
     */
    function compileDirective(scopeValues) {
        var html,
            scope,  // the scope of the element the directive is applied to
            $element;

        scope = $rootScope.$new();
        angular.extend(scope, scopeValues);

        html = '<div sd-user-privileges user="user"></div>';

        $element = $compile(html)(scope);
        scope.$digest();

        return $element;
    }

    beforeEach(function () {
        var $element,
            scopeValues,
            userPrivileges;

        userPrivileges = [{name: 'foo'}, {name: 'bar'}];

        scopeValues = {
            user: {
                privileges: userPrivileges,
                role: '€d1t0r'
            }
        };

        $element = compileDirective(scopeValues);
        isoScope = $element.isolateScope();
    });

    describe('on initialization', function () {
        it('fetches and stores the list of all privileges', function () {
            var serverResponse = {
                _items: [
                    {name: 'role_foo'},
                    {name: 'role_bar'}
                ]
            };

            expect(fakeEndpoints.privileges.query).toHaveBeenCalled();

            isoScope.privileges = [];
            queryDeferred.resolve(serverResponse);
            isoScope.$digest();

            expect(isoScope.privileges).toEqual(
                [{name: 'role_foo'}, {name: 'role_bar'}]
            );
        });

        it('fetches and stores the user\'s role object', function () {
            var serverResponse = {
                name: '€d1t0r',
                privileges: [
                    {name: 'create_content'}, {name: 'edit_content'}
                ]
            };

            expect(fakeEndpoints.roles.getById).toHaveBeenCalledWith('€d1t0r');

            isoScope.role = {};
            getByIdDeferred.resolve(serverResponse);
            isoScope.$digest();

            expect(isoScope.role).toEqual(serverResponse);
        });

        it('logs an error if fetching the user\'s role fails', function () {
            spyOn(console, 'log');

            getByIdDeferred.reject('Server error');
            isoScope.$digest();

            expect(console.log).toHaveBeenCalledWith('Server error');
        });

        it('stores the original list of user privileges', function () {
            expect(isoScope.origPrivileges).toEqual(
                [{name: 'foo'}, {name: 'bar'}]
            );
        });
    });

    describe('scope\'s save() method', function () {
        var api,
            saveDeferred;

        beforeEach(inject(function ($q, _api_) {
            api = _api_;
            saveDeferred = $q.defer();
            api.save.and.returnValue(saveDeferred.promise);
        }));

        it('saves user\'s privileges', function () {
            var userJohn = {
                name: 'John Doe',
                privileges: [{name: 'can_edit'}]
            };
            isoScope.user = userJohn;

            isoScope.save();

            expect(api.save).toHaveBeenCalledWith(
                'users',
                userJohn,
                {
                    privileges: [{name: 'can_edit'}]
                }
            );
        });

        it('updates the original priviliges list to the newly saved ones',
            function () {
                isoScope.user = {
                    name: 'John Doe',
                    privileges: [{name: 'manager'}, {name: 'reviewer'}]
                };

                isoScope.origPrivileges = [{name: 'editor'}];

                isoScope.save();
                saveDeferred.resolve();
                isoScope.$digest();

                expect(isoScope.origPrivileges).toEqual(
                    [{name: 'manager'}, {name: 'reviewer'}]
                );
            }
        );

        it('issues system notification on success', inject(function (notify) {
            spyOn(notify, 'success');

            isoScope.save();
            saveDeferred.resolve();
            isoScope.$digest();

            expect(notify.success).toHaveBeenCalledWith('Privileges updated.');
        }));

        it('marks the HTML form as pristine on success', function () {
            isoScope.userPrivileges.$pristine = false;

            isoScope.save();
            saveDeferred.resolve();
            isoScope.$digest();

            expect(isoScope.userPrivileges.$pristine).toBe(true);
        });

        it('does *not* mark the HTML form as pristine on error', function () {
            isoScope.userPrivileges.$pristine = false;

            isoScope.save();
            saveDeferred.reject({data: 'Server Error'});
            isoScope.$digest();

            expect(isoScope.userPrivileges.$pristine).toBe(false);
        });

        it('issues system notification on error', inject(function (notify) {
            spyOn(notify, 'error');

            isoScope.save();
            saveDeferred.reject({data: 'Server Error'});
            isoScope.$digest();

            expect(notify.error).toHaveBeenCalledWith(
                'Error. Privileges not updated.');
        }));
    });

    describe('scope\'s cancel() method', function () {
        it('restores user\'s original privilege setttings', function () {
            isoScope.user.privileges = [{name: 'aaa'}, {name: 'bbb'}];
            isoScope.origPrivileges = [{name: 'foo'}, {name: 'bar'}];

            isoScope.cancel();

            expect(isoScope.user.privileges).toEqual(
                [{name: 'foo'}, {name: 'bar'}]);
        });

        it('marks the corresponding HTML form as pristine', function () {
            isoScope.userPrivileges.$pristine = false;
            isoScope.cancel();
            expect(isoScope.userPrivileges.$pristine).toBe(true);
        });
    });

});
