'use strict';

describe('profile service', function() {
    beforeEach(module('superdesk.users.profile'));

    it('can get activity of all users', inject(function(profileService, api, $q) {
        spyOn(api, 'query').and.returnValue($q.when({}));
        profileService.getAllUsersActivity(5, 1);
        expect(api.query).toHaveBeenCalled();
        var args = api.query.calls.argsFor(0);
        expect(args[0]).toBe('activity');
        expect(args[1].where).toEqual({user: {$exists: true}, item: {$exists: true}});
    }));
});
