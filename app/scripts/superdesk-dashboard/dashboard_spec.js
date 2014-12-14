'use strict';

describe('dashboard', function() {

    var USER_URL = '/users/1';
    var USER = {
        _links: {self: {href: USER_URL}},
        _etag: '1'
    };

    beforeEach(module('templates'));
    beforeEach(module('superdesk.dashboard'));

    beforeEach(inject(function(session) {
        session.start({}, USER);
    }));

    it('can load user widgets', inject(function(workspace, api, $rootScope, $q) {
        spyOn(api, 'get').and.returnValue($q.when(USER));

        var widgets;
        workspace.load().then(function(_widgets) {
            widgets = _widgets.widgets;
        });

        $rootScope.$digest();
        expect(api.get).toHaveBeenCalledWith(USER_URL);
        expect(widgets.length).toBe(0);
    }));

    it('can add widget to user workspace', inject(function(workspace, api, $rootScope, $q) {

        var user = angular.extend(USER, {_etag: '2'});

        spyOn(api, 'get').and.returnValue($q.when(user));
        spyOn(api, 'save').and.returnValue($q.when(USER));

        workspace.load();
        $rootScope.$digest();
        workspace.save();
        $rootScope.$digest();

        expect(api.save).toHaveBeenCalledWith('users', user, {workspace: {widgets: []}});
    }));
});
