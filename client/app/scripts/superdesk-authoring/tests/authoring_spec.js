
'use strict';

describe('authoring', function() {

    var GUID = 'urn:tag:superdesk-1';
    var USER = 'user:1';
    var ITEM = {guid: GUID};

    beforeEach(module('superdesk.preferences'));
    beforeEach(module('superdesk.archive'));
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.publish'));
    beforeEach(module('superdesk.auth'));
    beforeEach(module('superdesk.workspace.content'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.privileges'));
    beforeEach(module('superdesk.desks'));

    beforeEach(inject(function($window) {
        $window.onbeforeunload = angular.noop;
    }));

    beforeEach(inject(function(preferencesService, desks, $q) {
        spyOn(preferencesService, 'get').and.returnValue($q.when({'items': ['urn:tag:superdesk-1']}));
        spyOn(preferencesService, 'update').and.returnValue($q.when({}));
        spyOn(preferencesService, 'getPrivileges').and.returnValue($q.when({}));
        spyOn(desks, 'fetchCurrentUserDesks').and.returnValue($q.when({_items: []}));
    }));

    beforeEach(inject(function($route) {
        $route.current = {params: {_id: GUID}};
    }));

    beforeEach(inject(function(session) {
        session.start({_id: 'sess'}, {_id: USER});
        expect(session.identity._id).toBe(USER);
    }));

    it('can open an item',
    inject(function(superdesk, api, lock, autosave, $injector, $q, $rootScope, $httpBackend) {
        var _item,
            lockedItem = angular.extend({_locked: false}, ITEM);

        spyOn(api, 'find').and.returnValue($q.when(ITEM));
        spyOn(lock, 'lock').and.returnValue($q.when(lockedItem));
        spyOn(autosave, 'open').and.returnValue($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item).then(function(resolvedItem) {
            _item = resolvedItem;
        });

        $rootScope.$digest();

        expect(api.find).toHaveBeenCalledWith('archive', GUID, jasmine.any(Object));
        expect(lock.lock).toHaveBeenCalledWith(ITEM);
        expect(autosave.open).toHaveBeenCalledWith(lockedItem);
        expect(_item.guid).toBe(GUID);
    }));

    it('does lock item only once',
    inject(function(superdesk, api, lock, autosave, session, $injector, $q, $rootScope) {
        var lockedItem = ITEM;
        lockedItem.lock_user = USER;

        spyOn(api, 'find').and.returnValue($q.when(lockedItem));

        $injector.invoke(superdesk.activity('authoring').resolve.item);
        $rootScope.$digest();
        expect(ITEM._locked).toBe(false);
    }));

    it('unlocks a locked item and locks by current user',
        inject(function(authoring, lock, $rootScope, $timeout, api, $q, $location) {

            spyOn(api, 'save').and.returnValue($q.when({}));
            spyOn(lock, 'unlock').and.returnValue($q.when({}));

            var lockedItem = {guid: GUID, _id: GUID, _locked: true, lock_user: 'user:5', task: 'desk:1'};
            var $scope = startAuthoring(lockedItem, 'edit');
            $rootScope.$digest();

            $scope.unlock();
            $timeout.flush(5000);
            $rootScope.$digest();
            expect($location.path(), '/authoring/' + $scope.item._id);
        }));

    it('can autosave and save an item', inject(function(api, $q, $timeout, $rootScope) {
        var $scope = startAuthoring({guid: GUID, _id: GUID, task: 'desk:1'}, 'edit'),
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
        var $scope = startAuthoring({headline: 'test', task: 'desk:1'}, 'edit');

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
     *
     * @param {object} item
     * @param {string} action
     * @returns {object}
     */
    function startAuthoring(item, action) {
        var $scope;

        inject(function($rootScope, $controller, superdesk, $compile) {
            $scope = $rootScope.$new();
            $controller(superdesk.activity('authoring').controller, {
                $scope: $scope,
                item: item,
                action: action
            });
            $compile(angular.element('<div sd-authoring-workspace><div sd-authoring></div></div>'))($scope);
        });

        return $scope;
    }

    describe('authoring service', function() {

        var confirmDefer;

        beforeEach(inject(function(confirm, lock, $q) {
            confirmDefer = $q.defer();
            spyOn(confirm, 'confirm').and.returnValue(confirmDefer.promise);
            spyOn(confirm, 'confirmPublish').and.returnValue(confirmDefer.promise);
            spyOn(confirm, 'confirmSaveWork').and.returnValue(confirmDefer.promise);
            spyOn(lock, 'unlock').and.returnValue($q.when());
        }));

        it('can check if an item is editable', inject(function(authoring, session) {
            expect(authoring.isEditable({})).toBe(false);
            expect(authoring.isEditable({lock_user: session.identity._id, lock_session: session.sessionId}))
                .toBe(true);
        }));

        it('can close a read-only item', inject(function(authoring, confirm, lock, $rootScope) {
            var done = jasmine.createSpy('done');
            authoring.close({}).then(done);
            $rootScope.$digest();

            expect(confirm.confirm).not.toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();
            expect(done).toHaveBeenCalled();
        }));

        it('can unlock on close editable item without changes made',
        inject(function(authoring, confirm, lock, $rootScope) {
            expect(authoring.isEditable(ITEM)).toBe(true);
            authoring.close(ITEM, false);
            $rootScope.$digest();
            expect(confirm.confirm).not.toHaveBeenCalled();
            expect(lock.unlock).toHaveBeenCalled();
        }));

        it('confirms if an item is dirty and saves',
        inject(function(authoring, confirm, lock, $q, $rootScope) {
            var edit = Object.create(ITEM);
            edit.headline = 'test';

            authoring.close(edit, ITEM, true);
            $rootScope.$digest();

            expect(confirm.confirm).toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();

            spyOn(authoring, 'save').and.returnValue($q.when());
            confirmDefer.resolve();
            $rootScope.$digest();

            expect(authoring.save).toHaveBeenCalledWith(ITEM, edit);
            expect(lock.unlock).toHaveBeenCalled();
        }));

        it('confirms if an item is dirty on opening new or existing item and not unlocking on save',
        inject(function(authoring, confirm, lock, $q, $rootScope) {
            var edit = Object.create(ITEM);
            edit.headline = 'test';

            authoring.close(edit, ITEM, true, true);
            $rootScope.$digest();

            expect(confirm.confirm).toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();

            spyOn(authoring, 'save').and.returnValue($q.when());
            confirmDefer.resolve();
            $rootScope.$digest();

            expect(authoring.save).toHaveBeenCalledWith(ITEM, edit);
            expect(lock.unlock).not.toHaveBeenCalled();
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

        it('confirms if an item is dirty and saves and publish',
        inject(function(authoring, api, confirm, lock, $q, $rootScope) {
            var edit = Object.create(ITEM);
            _.extend(edit, {
                _id: 1,
                headline: 'test',
                lock_user: 'user:1',
                state: 'submitted'
            });

            authoring.publishConfirmation(ITEM, edit, true, 'publish');
            $rootScope.$digest();

            expect(confirm.confirmPublish).toHaveBeenCalled();
            expect(lock.unlock).not.toHaveBeenCalled();

            spyOn(api, 'update').and.returnValue($q.when(_.extend({}, edit, {})));

            authoring.publish(edit);
            $rootScope.$digest();

            expect(api.update).toHaveBeenCalledWith('archive_publish', edit, {});
            expect(lock.unlock).toHaveBeenCalled();
        }));

        it('confirms if an item is dirty and save work in personal',
        inject(function(authoring, api, confirm, lock, $q, $rootScope) {
            var edit = Object.create(ITEM);
            _.extend(edit, {
                task: {desk: null, stage: null, user: 1},
                type: 'text',
                version: 1
            });

            authoring.saveWorkConfirmation(ITEM, edit, true, 'User is disabled');
            $rootScope.$digest();

            expect(confirm.confirmSaveWork).toHaveBeenCalled();

            spyOn(api, 'save').and.returnValue($q.when(_.extend({}, edit, {})));

            authoring.saveWork(edit);
            $rootScope.$digest();

            expect(api.save).toHaveBeenCalledWith('archive', {}, edit);

        }));
    });
});

describe('cropImage', function() {
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('templates'));

    it('can save crop', inject(function($q, $rootScope, urls, $http, $httpBackend, cropImage) {
        var item = {
            '_id': 'urn:newsml:localhost:2015-08-25T05:12:09.664870:4eeac2ab-a0e3-4fdc-b8fe-233ef9462ff1',
            'cropsize': {name: '4-3'}
        };
        var form = {
            'CropLeft': 0,
            'CropTop': 0,
            'CropRight': 800,
            'CropBottom': 600
        };
        var result;

        var _URL = 'http://master.dev.superdesk.org/api/archive';
        spyOn(urls, 'resource').and.returnValue($q.when(_URL));

        var POST_URL = _URL + '/' + item._id + '/crop/' + item.cropsize.name;

        $httpBackend.expectPOST(POST_URL, form).respond(201,
            {data: {'CropLeft': 0, 'CropTop': 0, 'CropRight': 800, 'CropBottom': 600}});

        cropImage.saveCrop(form, item).then(function(response) {
            result = response.data;
        });

        $httpBackend.flush();
        expect(result.CropLeft).toBe(0);
        expect(result.CropTop).toBe(0);
        expect(result.CropRight).toBe(800);
        expect(result.CropBottom).toBe(600);
        expect(urls.resource).toHaveBeenCalledWith('archive');
    }));
});

describe('autosave', function() {
    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('templates'));

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
    beforeEach(module('templates'));

    var user = {_id: 'user'};
    var sess = {_id: 'sess'};
    var anotherUser = {_id: 'another_user'};

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
        expect(lock.can_unlock({lock_user: anotherUser._id, lock_session: 'another_session'})).toBe(1);
    }));

    it('can unlock the item if user has no unlock privileges', inject(function(lock, privileges, $rootScope) {
        privileges.setUserPrivileges({unlock: 0});
        $rootScope.$digest();
        // testing if the user can unlock its own content.
        expect(lock.can_unlock({lock_user: user._id})).toBe(true);
        expect(lock.can_unlock({lock_user: user._id, lock_session: 'another_session'})).toBe(true);
        expect(lock.can_unlock({lock_user: anotherUser._id, lock_session: 'another_session'})).toBe(0);
    }));
});

describe('authoring actions', function() {
    var userDesks = [{'_id': 'desk1'}, {'_id': 'desk2'}];

    /**
    * Assert the actions
    * @param {Object} actions : actions to be asserted.
    * @param {Object} keys : keys to be truthy.
    */
    function allowedActions(actions, keys) {
        _.forOwn(actions, function(value, key) {

            //console.log('checking state for', key, value, _.contains(keys, key));

            if (_.contains(keys, key)) {
                expect(value).toBeTruthy();
            } else {
                expect(value).toBeFalsy();
            }
        });
    }

    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.desks'));
    beforeEach(module('templates'));

    beforeEach(inject(function(desks, $q) {
        spyOn(desks, 'fetchCurrentUserDesks').and.returnValue($q.when({_items: userDesks}));
    }));

    it('can perform actions if the item is located on the personal workspace',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'draft',
                'marked_for_not_publication': false,
                'type': 'text'
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'copy', 'view',
                    'spike', 'package_item', 'multi_edit']);
        }));

    it('can perform actions if the item is located on the desk',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'submitted',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                    'mark_item', 'package_item', 'multi_edit', 'publish']);
        }));

    it('cannot publish if user does not have publish privileges on the desk',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'submitted',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': false
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                'mark_item', 'package_item', 'multi_edit']);
        }));

    it('can only view the item if the user does not have desk membership',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'submitted',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk3'
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['view', 'duplicate']);
        }));

    it('can only view the item if the item is killed',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'killed',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['view']);
        }));

    it('can only view item if the item is spiked',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'spiked',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['view', 'unspike']);
        }));

    it('Cannot perform new take if more coming is true or take is not last take on the desk',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': true
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['save', 'edit', 'duplicate', 'view', 'spike',
                'mark_item', 'package_item', 'multi_edit', 'publish']);

            item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'takes': {
                    'last_take': 'take2'
                }
            };

            itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['save', 'edit', 'duplicate', 'view',
                'mark_item', 'package_item', 'multi_edit', 'publish']);
        }));

    it('Can peform new take',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                'mark_item', 'package_item', 'multi_edit', 'publish']);

            item = {
                '_id': 'test',
                'state': 'published',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'archive_item': {
                    '_id': 'test',
                    'state': 'published',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'takes': {
                        'last_take': 'test'
                    }
                }
            };

            itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'duplicate', 'view',
                'mark_item', 'package_item', 'multi_edit', 'correct', 'kill', 're_write']);
        }));

    it('Can perform correction or kill on published item',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'published',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 10,
                'archive_item': {
                    '_id': 'test',
                    'state': 'published',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'more_coming': false,
                    '_current_version': 10
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'duplicate', 'view',
                'mark_item', 'package_item', 'multi_edit', 'correct', 'kill', 're_write']);
        }));

    it('Cannot perform correction or kill on published item without privileges',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'published',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 10,
                'archive_item': {
                    '_id': 'test',
                    'state': 'published',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'more_coming': false,
                    '_current_version': 10
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': false,
                'kill': false
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'duplicate', 'view',
                'mark_item', 'package_item', 'multi_edit', 're_write']);
        }));

    it('Can only view if the item is not the current version',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'published',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 8,
                'archive_item': {
                    '_id': 'test',
                    'state': 'published',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'more_coming': false,
                    '_current_version': 10
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['view']);
        }));

    it('Can only view and deschedule if the item is scheduled',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'scheduled',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 8,
                'archive_item': {
                    '_id': 'test',
                    'state': 'scheduled',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'more_coming': false,
                    '_current_version': 8
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['view', 'deschedule']);
        }));

    it('Can only package if the item is not a take package',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'published',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 8,
                'archive_item': {
                    '_id': 'test',
                    'state': 'published',
                    'marked_for_not_publication': false,
                    'type': 'text',
                    'task': {
                        'desk': 'desk1'
                    },
                    'more_coming': false,
                    '_current_version': 8
                }
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true,
                'package_item': false
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['correct', 'kill', 'new_take', 're_write',
                'mark_item', 'duplicate', 'view', 'package_item', 'multi_edit']);
        }));

    it('Cannot send item if the version is zero',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 0
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true,
                'package_item': false,
                'move': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                    'mark_item', 'package_item', 'multi_edit', 'publish']);
        }));

    it('Cannot send item if the no move privileges',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 1
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true,
                'package_item': false,
                'move': false
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                    'mark_item', 'package_item', 'multi_edit', 'publish']);
        }));

    it('Can send item if the version greater then zero',
        inject(function(privileges, desks, authoring, $q, $rootScope) {
            var item = {
                '_id': 'test',
                'state': 'in_progress',
                'marked_for_not_publication': false,
                'type': 'text',
                'task': {
                    'desk': 'desk1'
                },
                'more_coming': false,
                '_current_version': 1
            };

            var userPrivileges = {
                'duplicate': true,
                'mark_item': false,
                'spike': true,
                'unspike': true,
                'mark_for_highlights': true,
                'unlock': true,
                'publish': true,
                'correct': true,
                'kill': true,
                'package_item': false,
                'move': true
            };

            privileges.setUserPrivileges(userPrivileges);
            $rootScope.$digest();
            var itemActions = authoring.itemActions(item);
            allowedActions(itemActions, ['new_take', 'save', 'edit', 'duplicate', 'view', 'spike',
                    'mark_item', 'package_item', 'multi_edit', 'publish', 'send']);
        }));

    describe('authoring workspace controller', function() {
        var ctrl, scope;

        beforeEach(inject(function($controller, $rootScope) {
            scope = $rootScope.$new();
            scope.flags = {};
            ctrl = $controller('AuthoringWorkspace', {$scope: scope});
        }));

        it('can edit item', inject(function() {
            var item = {};

            expect(scope.flags.authoring).toBeFalsy();

            ctrl.edit(item);
            expect(ctrl.item).toBe(item);
            expect(ctrl.getItem()).toBe(item);
            expect(scope.flags.authoring).toBeTruthy();

            ctrl.close();
            expect(ctrl.item).toBe(null);
            expect(ctrl.getItem()).toBe(null);
            expect(scope.flags.authoring).toBeFalsy();
        }));
    });
});
