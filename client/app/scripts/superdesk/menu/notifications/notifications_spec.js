'use strict';

describe('notifications', function() {

    var notifications = {_items: [
        {read: {foo: 0, bar: 1}},
        {read: {foo: 1, bar: 1}},
        {read: {foo: 1, bar: 0}}
    ]};

    beforeEach(module('superdesk.api'));
    beforeEach(module('superdesk.menu.notifications'));

    beforeEach(inject(function(api, $q) {
        spyOn(api, 'query').and.returnValue($q.when(notifications));
    }));

    beforeEach(inject(function(session, $q) {
        spyOn(session, 'getIdentity').and.returnValue($q.reject());
    }));

    it('can fetch content notifications', inject(function(userNotifications, session, api, $rootScope) {
        session.identity = {_id: 'foo', user_type: 'user'};

        expect(userNotifications._items).toBe(null);
        expect(userNotifications.unread).toBe(0);

        userNotifications.reload();
        $rootScope.$digest();

        expect(userNotifications._items.length).toBe(3);
        expect(userNotifications.unread).toBe(1);

        expect(api.query).toHaveBeenCalled();

        var args = api.query.calls.argsFor(0);
        expect(args[0]).toBe('activity');

        var query = args[1].where;
        expect(query.user).toEqual({$exists: true});
        expect(query.item).toEqual({$exists: true});
    }));

    it('can fetch system notification for admins',
    inject(function(userNotifications, session, api, $rootScope) {
        session.identity = {_id: 'foo', user_type: 'administrator'};
        userNotifications.reload();
        $rootScope.$digest();
        var args = api.query.calls.argsFor(0);
        var query = args[1].where;
        expect(query.user).toBeUndefined();
        expect(query.item).toBeUndefined();
    }));
});
