
'use strict';

describe('desks service', function() {

	var USER_URL = 'users/1';

	beforeEach(module('superdesk.desks'));

	it('can fetch current user desks', inject(function(desks, session, api, preferencesService, $rootScope, $q) {
		spyOn(session, 'getIdentity').and.returnValue($q.when({_links: {self: {href: USER_URL}}}));
		spyOn(api, 'get').and.returnValue($q.when({_items: [{name: 'sport'}, {name: 'news'}]}));
		spyOn(preferencesService, 'get').and.returnValue($q.when([]));

		var userDesks;
		desks.fetchCurrentUserDesks().then(function(_userDesks) {
			userDesks = _userDesks;
		});

		$rootScope.$apply();

		expect(userDesks.length).toBe(2);
	}));

	it('can save desk changes', inject(function(desks, api, $q) {
		spyOn(api, 'save').and.returnValue($q.when({}));
		desks.save({}, {});
		expect(api.save).toHaveBeenCalledWith('desks', {}, {});
	}));

	it('can remove a desk', inject(function(desks, api, $q) {
		spyOn(api, 'remove').and.returnValue($q.when({}));
		desks.remove({});
		expect(api.remove).toHaveBeenCalledWith({});
	}));
});
