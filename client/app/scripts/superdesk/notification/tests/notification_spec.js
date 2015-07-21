'use strict';
describe('Reload Service', function() {
    beforeEach(module('superdesk.notification'));
    var USER_URL = '/users/1';
    var USER = {
        _links: {self: {href: USER_URL}},
        _etag: '2',
        _id: '1'
    };

    var rootScope, reloadService, msg;
    beforeEach(function() {
        inject(function($rootScope, _reloadService_, session, $q, api, preferencesService, desks, $window) {
            rootScope = $rootScope;
            reloadService = _reloadService_;
            session.start({}, USER);

            spyOn(session, 'getIdentity').and.returnValue($q.when({_links: {self: {href: USER_URL}}}));
            spyOn(api, 'get').and.returnValue($q.when({_items: [
                {_id: '5567ff31102454c7bac47644'},
                {_id: '55394997102454b5ea111bd5'}
            ]}));
            spyOn(preferencesService, 'get').and.returnValue($q.when([]));
            spyOn(preferencesService, 'update');

            desks.fetchCurrentUserDesks().then(function(_userDesks) {
                reloadService.userDesks = _userDesks._items;
            });

            rootScope.$apply();
            expect(reloadService.userDesks.length).toBe(2);
        });
    });

    it('can check reloadEvents on raised event for desk', inject(function() {
        msg = {
            event: 'desk_membership_revoked',
            extra: {
                        desk_id: '5567ff31102454c7bac47644',
                        user_ids: ['1']
                    }
        };

        var reload = spyOn(reloadService, 'reload');
        rootScope.$broadcast('reload', msg);
        expect(reload).toHaveBeenCalledWith(Object({reload: true, message: 'User removed from desk'}));
        expect(reloadService.result.reload).toBe(true);
    }));

    it('can check reloadEvents on raised event for stage', inject(function() {
        msg = {
            event: 'stage',
            extra: {
                        desk_id: '5567ff31102454c7bac47644',
                        user_ids: ['1']
                    }
        };

        var reload = spyOn(reloadService, 'reload');
        rootScope.$broadcast('reload', msg);
        expect(reload).toHaveBeenCalledWith(Object({
            reload: true,
            message: 'Stage is created/updated/deleted'
        }));
        expect(reloadService.result.reload).toBe(true);
    }));
});
