'use strict';

describe('notifications', function() {

    var notifications = {_items: [
        {read: {foo: 0, bar: 1}},
        {read: {foo: 1, bar: 1}},
        {read: {foo: 1, bar: 0}}
    ]};

    beforeEach(module('superdesk.menu.notifications'));
    beforeEach(module(function($provide) {
        $provide.factory('api', function($q) {
            return function() {
                return {
                    query: function() {
                        return $q.when(notifications);
                    }
                };
            };
        });
    }));

    beforeEach(inject(function(session) {
        session.identity = {_id: 'foo'};
    }));

    it('can fetch notifications', inject(function(userNotifications, $rootScope) {

        expect(userNotifications._items).toBe(null);
        expect(userNotifications.unread).toBe(0);

        var resolved = jasmine.createSpy('resolved');
        userNotifications.reload().then(function() {
            resolved();
            expect(userNotifications._items.length).toBe(3);
            expect(userNotifications.unread).toBe(1);
        });

        $rootScope.$digest();

        expect(resolved).toHaveBeenCalled();
    }));
});
