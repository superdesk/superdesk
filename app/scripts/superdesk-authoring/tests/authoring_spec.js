
'use strict';

describe('authoring', function() {

    var GUID = 'urn:tag:superdesk-1';
    var USER = 'user:1';
    var item = {guid: GUID};

    beforeEach(module('superdesk.services.preferencesService'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.auth'));
    beforeEach(module('superdesk.mocks'));

    beforeEach(inject(function($window) {
        $window.onbeforeunload = angular.noop;
    }));

    beforeEach(inject(function(preferencesService, $q) {
            spyOn(preferencesService, 'getPreferences').andReturn($q.when({}));
            spyOn(preferencesService, 'get').andReturn($q.when({'items':[]}));
            spyOn(preferencesService, 'update').andReturn($q.when({}));
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

    it('can autosave and save an item', inject(function(superdesk, api, $q, $timeout, $controller, $rootScope) {
        var scope = $rootScope.$new(),
            headline = 'test headline';

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

    it('can use a previously created autosave', inject(function($rootScope, $controller, superdesk) {
        var scope = $rootScope.$new();
        $controller(superdesk.activity('authoring').controller, {item: {_autosave: {headline: 'test'}}, $scope: scope});
        expect(scope.item._autosave.headline).toBe('test');
        expect(scope.item.headline).toBe('test');
    }));

    it('can save while item is being autosaved', inject(function($rootScope, $timeout, $controller, $q, api, superdesk) {
        var $scope = $rootScope.$new();
        $controller(superdesk.activity('authoring').controller, {item: {headline: 'test'}, $scope: $scope});
        $scope.item.body_html = 'test';
        $rootScope.$digest();

        $timeout.flush(1000);

        spyOn(api, 'save').andReturn($q.when({}));
        $scope.save();
        $rootScope.$digest();
        expect($scope.saving).toBe(false);

        $timeout.flush(5000);
        expect($scope.item._autosave).toBe(null);
    }));
});

describe('autosave', function() {
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));

    it('can fetch an autosave for not locked item', inject(function(autosave, api, $q, $rootScope) {
        spyOn(api, 'find').andReturn($q.when({}));
        autosave.open({_locked: false, _id: 1});
        $rootScope.$digest();
        expect(api.find).toHaveBeenCalledWith('archive_autosave', 1);
    }));

    it('will skip autosave fetch when item is locked', inject(function(autosave, api, $rootScope) {
        spyOn(api, 'find');
        autosave.open({_locked: true});
        $rootScope.$digest();
        expect(api.find).not.toHaveBeenCalled();
    }));

    it('can create an autosave', inject(function(autosave, api, $q, $timeout, $rootScope) {
        var item = {_id: 1, _etag: 'x'};
        spyOn(api, 'save').andReturn($q.when({_id: 2}));
        autosave.save(item, {headline: 'test'});
        $rootScope.$digest();
        expect(api.save).not.toHaveBeenCalled();
        $timeout.flush(5000);
        expect(api.save).toHaveBeenCalledWith('archive_autosave', {}, {_id: 1, headline: 'test'});
        expect(item._autosave._id).toBe(2);
        expect(item.headline).toBe('test');
    }));
});
