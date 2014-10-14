
'use strict';

describe('authoring', function() {

    var GUID = 'urn:tag:superdesk-1';
    var USER = 'user:1';
    var item = {guid: GUID};

    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.auth'));

    beforeEach(module(function($provide) {
        // avoid confirmation in tests
        $provide.service('$window', function() {});
    }));

    beforeEach(inject(function($route) {
        $route.current = {params: {_id: GUID}};
    }));

    beforeEach(inject(function(session) {
        session.mock(USER);
        expect(session.identity._id).toBe(USER);
    }));

    it('can open an item', inject(function(superdesk, api, lock, autosave, $injector, $q, $rootScope) {
        var _item,
            lockedItem = angular.extend({_locked: false}, item);

        spyOn(api, 'find').andReturn($q.when(item));
        spyOn(lock, 'lock').andReturn($q.when(lockedItem));
        spyOn(autosave, 'open').andReturn($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item).then(function(resolvedItem) {
            _item = resolvedItem;
        });

        $rootScope.$digest();

        expect(api.find).toHaveBeenCalledWith('archive', GUID);
        expect(lock.lock).toHaveBeenCalledWith(item);
        expect(autosave.open).toHaveBeenCalledWith(lockedItem);
        expect(_item.guid).toBe(GUID);
    }));

    it('does lock item only once', inject(function(superdesk, api, lock, autosave, session, $injector, $q, $rootScope) {
        var lockedItem = item;
        lockedItem.lock_user = USER;

        spyOn(api, 'find').andReturn($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item);
        $rootScope.$digest();
        expect(item._locked).toBe(false);
    }));

    it('can autosave and save an item', inject(function(superdesk, api, desks, $q, $timeout, $controller, $rootScope) {
        var scope = $rootScope.$new(),
            headline = 'test headline';

        spyOn(desks, 'initialize').andReturn($q.reject());

        $controller(superdesk.activity('authoring').controller, {item: item, $scope: scope});
        expect(scope.dirty).toBe(false);
        expect(scope.item.guid).toBe(GUID);

        // edit
        scope.item.headline = headline;
        $rootScope.$digest();
        expect(scope.dirty).toBe(true);
        expect(scope.saving).toBe(true);

        // autosave
        spyOn(api, 'save').andReturn($q.when({}));
        $timeout.flush(5000);
        expect(api.save).toHaveBeenCalled();

        // save
        scope.save();
        $rootScope.$digest();
        expect(scope.dirty).toBe(false);
        expect(api.save).toHaveBeenCalled();
    }));
});
