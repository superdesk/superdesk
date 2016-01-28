'use strict';

describe('user notifications', function() {

    var notifications = {_items: [
        {recipients: [{'user_id': 'foo', 'read': 0}, {'user_id': 'bar', 'read': 1}]},
        {recipients: [{'user_id': 'foo', 'read': 1}, {'user_id': 'bar', 'read': 1}]},
        {recipients: [{'user_id': 'foo', 'read': 1}, {'user_id': 'bar', 'read': 0}]}
    ]};

    beforeEach(module('superdesk.session'));
    beforeEach(module('superdesk.api'));
    beforeEach(module('superdesk.menu.notifications'));

    beforeEach(inject(function(api, $q) {
        spyOn(api, 'query').and.returnValue($q.when(notifications));
    }));

    beforeEach(inject(function(session, $q) {
        spyOn(session, 'getIdentity').and.returnValue($q.reject());
    }));

    it('can fetch user notifications', inject(function(userNotifications, session, api, $rootScope) {
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

describe('desk notifications', function() {

    var notifications = {_items: [
        {recipients: [{'desk_id': 'desk1', 'read': 0}, {'desk_id': 'desk2', 'read': 1}]},
        {recipients: [{'desk_id': 'desk1', 'read': 1}, {'desk_id': 'desk2', 'read': 0}]},
        {recipients: [{'desk_id': 'desk1', 'read': 1}, {'desk_id': 'desk2', 'read': 0}]}
    ]};

    beforeEach(module('superdesk.session'));
    beforeEach(module('superdesk.api'));
    beforeEach(module('superdesk.menu.notifications'));

    beforeEach(inject(function(api, $q) {
        spyOn(api, 'query').and.returnValue($q.when(notifications));
    }));

    it('can fetch desk notifications', inject(function(deskNotifications, session, api, $rootScope) {
        session.identity = {_id: 'foo', user_type: 'user'};

        expect(deskNotifications._items).toEqual({});
        expect(deskNotifications.getUnreadCount('desk1')).toBe(0);

        deskNotifications.reload();
        $rootScope.$digest();

        expect(deskNotifications._items.desk1.length).toBe(3);
        expect(deskNotifications.unread).toEqual({desk1: 1, desk2: 2});

        expect(api.query).toHaveBeenCalled();

        var args = api.query.calls.argsFor(0);
        expect(args[0]).toBe('activity');
    }));
});
