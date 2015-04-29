
'use strict';

describe('authoring', function() {

    var GUID = 'urn:tag:superdesk-1';
    var USER = 'user:1';
    var item = {guid: GUID};

    beforeEach(module('superdesk.preferences'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.publish'));
    beforeEach(module('superdesk.auth'));
    beforeEach(module('superdesk.workspace.content'));
    beforeEach(module('superdesk.mocks'));

    beforeEach(inject(function($window) {
        $window.onbeforeunload = angular.noop;
    }));

    beforeEach(inject(function(preferencesService, $q) {
        spyOn(preferencesService, 'get').and.returnValue($q.when({'items':['urn:tag:superdesk-1']}));
        spyOn(preferencesService, 'update').and.returnValue($q.when({}));
    }));

    beforeEach(inject(function($route) {
        $route.current = {params: {_id: GUID}};
    }));

    beforeEach(inject(function(session) {
        session.start({_id: 'sess'}, {_id: USER});
        expect(session.identity._id).toBe(USER);
    }));

    it('can open an item', inject(function(superdesk, api, lock, autosave, $injector, $q, $rootScope, $httpBackend) {
        var _item,
            lockedItem = angular.extend({_locked: false}, item);

        spyOn(api, 'find').and.returnValue($q.when(item));
        spyOn(lock, 'lock').and.returnValue($q.when(lockedItem));
        spyOn(autosave, 'open').and.returnValue($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item).then(function(resolvedItem) {
            _item = resolvedItem;
        });

        $rootScope.$digest();

        expect(api.find).toHaveBeenCalledWith('archive', GUID, jasmine.any(Object));
        expect(lock.lock).toHaveBeenCalledWith(item);
        expect(autosave.open).toHaveBeenCalledWith(lockedItem);
        expect(_item.guid).toBe(GUID);
    }));

    it('does lock item only once', inject(function(superdesk, api, lock, autosave, session, $injector, $q, $rootScope) {
        var lockedItem = item;
        lockedItem.lock_user = USER;

        spyOn(api, 'find').and.returnValue($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item);
        $rootScope.$digest();
        expect(item._locked).toBe(false);
    }));

    it('unlocks a locked item and locks by current user', inject(function(authoring, lock, $rootScope, $timeout, api, $q) {
        spyOn(api, 'save').and.returnValue($q.when({}));

        var lockedItem = {guid: GUID, _locked: true, lock_user: 'user:5'};
        var $scope = startAuthoring(lockedItem, 'edit');
        $rootScope.$digest();

        $scope.unlock();
        $timeout.flush(5000);
        $rootScope.$digest();

        expect(lock.isLocked($scope.item)).toBe(false);
        expect($scope.item.lock_user).toBe(USER);
    }));

    it('can autosave and save an item', inject(function(api, $q, $timeout, $rootScope) {
        var $scope = startAuthoring(item, 'edit'),
            headline = 'test headline';

        expect($scope.dirty).toBe(false);
        expect($scope.item.guid).toBe(GUID);

        // edit
        $scope.item.headline = headline;
        $scope.autosave($scope.item);
        expect($scope.dirty).toBe(true);

        // autosave
        spyOn(api, 'save').and.returnValue($q.when({}));
        $timeout.flush(5000);
        expect(api.save).toHaveBeenCalled();

        // save
        $scope.save();
        $rootScope.$digest();
        expect($scope.dirty).toBe(false);
        expect(api.save).toHaveBeenCalled();
    }));

    it('can use a previously created autosave', inject(function() {
        var $scope = startAuthoring({_autosave: {headline: 'test'}}, 'edit');
        expect($scope.item._autosave.headline).toBe('test');
        expect($scope.item.headline).toBe('test');
    }));

    it('can save while item is being autosaved', inject(function($rootScope, $timeout, $q, api) {
        var $scope = startAuthoring({headline: 'test'}, 'edit');

        $scope.item.body_html = 'test';
        $rootScope.$digest();
        $timeout.flush(1000);

        spyOn(api, 'save').and.returnValue($q.when({}));
        $scope.save();
        $rootScope.$digest();

        $timeout.flush(5000);
        expect($scope.item._autosave).toBeNull();
    }));

    it('can open item stage', inject(function($rootScope, $location, desks, superdesk) {
        var $scope = startAuthoring({headline: 'test'}, 'edit');
        $scope.item.task = {desk: 1, stage: 2};

        spyOn(desks, 'setWorkspace');
        spyOn(superdesk, 'intent');

        $scope.openStage();

        expect(desks.setWorkspace).toHaveBeenCalledWith(1, 2);
        expect(superdesk.intent).toHaveBeenCalledWith('view', 'content');
    }));

    /**
     * Start authoring ctrl for given item.
     */
    function startAuthoring(item, action) {
        var $scope;

        inject(function($rootScope, $controller, superdesk, $compile) {
            $scope = $rootScope.$new();
            $controller(superdesk.activity('authoring').controller, {$scope: $scope, item: item, action: action});
            $compile(angular.element('<div sd-authoring></div>'))($scope);
        });

        return $scope;
    }

    describe('authoring service', function() {

        var confirmDefer;

        beforeEach(inject(function(confirm, lock, $q) {
            confirmDefer = $q.defer();
            spyOn(confirm, 'confirm').and.returnValue(confirmDefer.promise);
            spyOn(confirm, 'confirmPublish').and.returnValue(confirmDefer.promise);
            spyOn(lock, 'unlock').and.returnValue($q.when());
        }));

        it('can check if an item is editable', inject(function(authoring, session) {
            expect(authoring.isEditable({})).toBe(false);
            expect(authoring.isEditable({lock_user: session.identity._id, lock_session: session.sessionId})).toBe(true);
        }));

        it('can close a read-only item', inject(function(authoring, confirm, lock, $rootScope) {
            var done = jasmine.createSpy('done') ;
            authoring.close({}).then(done);
            $rootScope.$digest();

            expect(confirm.confirm).not.toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();
            expect(done).toHaveBeenCalled();
        }));

        it('can unlocks on close editable item without changes made', inject(function(authoring, confirm, lock, $rootScope) {
            expect(authoring.isEditable(item)).toBe(true);
            authoring.close(item, false);
            $rootScope.$digest();
            expect(confirm.confirm).not.toHaveBeenCalled();
            expect(lock.unlock).toHaveBeenCalled();
        }));

        it('confirms if an item is dirty and saves', inject(function(authoring, confirm, lock, $q, $rootScope) {
            var edit = Object.create(item);
            edit.headline = 'test';

            authoring.close(edit, item, true);
            $rootScope.$digest();

            expect(confirm.confirm).toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();

            spyOn(authoring, 'save').and.returnValue($q.when());
            confirmDefer.resolve();
            $rootScope.$digest();

            expect(authoring.save).toHaveBeenCalledWith(item, edit);
            expect(lock.unlock).toHaveBeenCalled();
        }));

        it('can unlock an item', inject(function(authoring, session, confirm, autosave) {
            var item = {lock_user: session.identity._id, lock_session: session.sessionId};
            expect(authoring.isEditable(item)).toBe(true);
            spyOn(confirm, 'unlock');
            spyOn(autosave, 'stop');
            authoring.unlock(item);
            expect(authoring.isEditable(item)).toBe(false);
            expect(confirm.unlock).toHaveBeenCalled();
            expect(autosave.stop).toHaveBeenCalled();
        }));
        it('can publish items', inject(function(authoring, api, $q) {
            var item = {_id: 1, state: 'submitted'};
            spyOn(api, 'update').and.returnValue($q.when());
            authoring.publish(item);
            expect(api.update).toHaveBeenCalledWith('archive_publish', item, {});
        }));

        it('confirms if an item is dirty and saves and publish', inject(function(authoring, api, confirm, lock, $q, $rootScope) {
            var edit = Object.create(item);
            _.extend(edit, {
                _id: 1,
                headline: 'test',
                lock_user: 'user:1',
                state: 'submitted'
            });

            authoring.publishConfirmation(item, edit, true);
            $rootScope.$digest();

            expect(confirm.confirmPublish).toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();

            spyOn(api, 'update').and.returnValue($q.when(_.extend({}, edit, {})));

            authoring.publish(edit);
            $rootScope.$digest();

            expect(api.update).toHaveBeenCalledWith('archive_publish', edit, {});
            expect(lock.unlock).toHaveBeenCalled();
        }));
    });
});

describe('autosave', function() {
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));

    it('can fetch an autosave for not locked item', inject(function(autosave, api, $q, $rootScope) {
        spyOn(api, 'find').and.returnValue($q.when({}));
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
        var edit = Object.create(item);
        edit.headline = 'test';
        spyOn(api, 'save').and.returnValue($q.when({_id: 2}));
        autosave.save(edit);
        $rootScope.$digest();
        expect(api.save).not.toHaveBeenCalled();
        $timeout.flush(5000);
        expect(api.save).toHaveBeenCalledWith('archive_autosave', {}, {_id: 1, headline: 'test'});
        expect(item._autosave._id).toBe(2);
        expect(edit.headline).toBe('test');
        expect(item.headline).not.toBe('test');
    }));

    it('can save multiple items', inject(function(autosave, api, $q, $timeout, $rootScope) {
        var item1 = {_id: 1, _etag: '1'},
            item2 = {_id: 2, _etag: '2'};
        spyOn(api, 'save').and.returnValue($q.when({}));

        autosave.save(_.create(item1));
        $timeout.flush(1500);

        autosave.save(_.create(item2));
        $timeout.flush(2500);

        expect(api.save).toHaveBeenCalled();
        expect(api.save.calls.count()).toBe(1);

        $timeout.flush(5000);
        expect(api.save.calls.count()).toBe(2);
    }));
});

describe('lock service', function() {
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));

    var user = {_id: 'user'};
    var sess = {_id: 'sess'};
    var another_user = {_id: 'another_user'};

    beforeEach(inject(function(session) {
        session.start(sess, user);
    }));

    it('can test if item is locked', inject(function(lock) {
        expect(lock.isLocked({})).toBe(false);
        expect(lock.isLocked({lock_user: '1'})).toBe(true);
    }));

    it('can detect lock by same user and different session', inject(function(lock) {
        expect(lock.isLocked({lock_user: 'user'})).toBe(false);
        expect(lock.isLocked({lock_user: 'user', lock_session: 'other_sess'})).toBe(true);
    }));

    it('can use lock_user dict', inject(function(lock) {
        expect(lock.isLocked({lock_user: {_id: 'user'}})).toBe(false);
    }));

    it('can unlock the item if user has unlock privileges', inject(function(lock, privileges, $rootScope) {
        privileges.setUserPrivileges({unlock: 1});
        $rootScope.$digest();
        // testing if the user can unlock its own content.
        expect(lock.can_unlock({lock_user: user._id})).toBe(true);
        expect(lock.can_unlock({lock_user: user._id, lock_session: 'another_session'})).toBe(true);
        expect(lock.can_unlock({lock_user: another_user._id, lock_session: 'another_session'})).toBe(1);
    }));

    it('can unlock the item if user has no unlock privileges', inject(function(lock, privileges, $rootScope) {
        privileges.setUserPrivileges({unlock: 0});
        $rootScope.$digest();
        // testing if the user can unlock its own content.
        expect(lock.can_unlock({lock_user: user._id})).toBe(true);
        expect(lock.can_unlock({lock_user: user._id, lock_session: 'another_session'})).toBe(true);
        expect(lock.can_unlock({lock_user: another_user._id, lock_session: 'another_session'})).toBe(0);
    }));
});
