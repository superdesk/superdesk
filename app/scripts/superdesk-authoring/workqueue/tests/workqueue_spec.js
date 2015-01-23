
'use strict';

describe('workqueue', function() {

    beforeEach(module('superdesk.authoring.workqueue'));

    it('loads locked items of current user', inject(function(workqueue, api, session, $q, $rootScope) {
        var items, USER_ID = 'u1';

        spyOn(api, 'query').and.returnValue($q.when({_items: [{}]}));
        spyOn(session, 'getIdentity').and.returnValue($q.when({_id: USER_ID}));

        workqueue.fetch().then(function() {
            items = workqueue.items;
        });

        $rootScope.$apply();

        expect(items.length).toBe(1);
        expect(items).toBe(workqueue.items);
        expect(api.query).toHaveBeenCalledWith('archive', {source: {filter: {term: {lock_user: USER_ID}}}});
        expect(session.getIdentity).toHaveBeenCalled();
    }));

    it('can update single item', inject(function(workqueue, api, $q, $rootScope) {
        spyOn(api, 'find').and.returnValue($q.when({_etag: 'xy'}));

        workqueue.items = [{_id: '1'}];
        workqueue.updateItem('1');

        $rootScope.$digest();

        expect(api.find).toHaveBeenCalledWith('archive', '1');
        expect(workqueue.items[0]._etag).toBe('xy');
    }));
});
