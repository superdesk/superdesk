
'use strict';

describe('user import', function() {

    beforeEach(module('superdesk.users.import'));
    beforeEach(module('superdesk.mocks'));

    it('can import a user', inject(function($q, userImport, api) {
        var model = {username: 'foo', password: 'bar', profile_to_import: 'baz'};
        spyOn(api, 'save').and.returnValue($q.when({}));
        userImport.importUser(model);
        expect(api.save).toHaveBeenCalledWith('import_profile', model);
    }));

    it('can return an error', inject(function($q, $rootScope, userImport, api) {
        var success = jasmine.createSpy('success'),
            error = jasmine.createSpy('error');

        spyOn(api, 'save').and.returnValue($q.reject({status: 404, data: {_message: 'test'}}));

        userImport.importUser({}).then(success, error);
        $rootScope.$digest();

        expect(success).not.toHaveBeenCalled();
        expect(error).toHaveBeenCalledWith({profile_to_import: 1, message: 'test'});
    }));
});
