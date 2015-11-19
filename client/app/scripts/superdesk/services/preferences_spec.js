'use strict';

describe('Preferences Service', function() {

    beforeEach(module('superdesk.preferences'));
    beforeEach(module('superdesk.api'));

    var preferencesService,
        testPreferences = {
            'active_privileges': {'privilege1': 1, 'privilege2': 0},
            'user_preferences': {
                'archive:view': {
                    'default': 'mgrid',
                    'label': 'Users archive view format',
                    'type': 'string',
                    'category': 'archive',
                    'allowed': [
                        'mgrid',
                        'compact'
                    ],
                    'view': 'mgrid'
                },
                'feature:preview': {
                    'default': false,
                    'type': 'bool',
                    'category': 'feature',
                    'enabled': true,
                    'label': 'test'
                },
                'email:notification': {
                    'default': true,
                    'category': 'notifications',
                    'enabled': true,
                    'type': 'bool',
                    'label': 'Send notifications via email'
                }
            },
            'session_preferences': {
                'desk:items': [],
                'pinned:items': [],
                'scratchpad:items': [
                    '/archive/urn:newsml:a0cca6c9-fe94-46ed-9ce7-aab9361ff6b8',
                    '/archive/urn:newsml:a0cca6c9-fe94-46ed-9ce7-aab9361ff6b8'
                ]
            }
        };

    var testUncachedPreferences = {'user_preferences': {'feature:preview': {'enabled': false}}};

    var update = {
        'feature:preview': {
            'default': false,
            'enabled': false,
            'label': 'Test Label',
            'type': 'bool',
            'category': 'feature'
        }
    };

    beforeEach(inject(function(api, $q) {
        spyOn(api, 'find').and.callFake(function(resource, id, params, cache) {
            if (cache) {
                return $q.when(testPreferences);
            } else {
                return $q.when(testUncachedPreferences);
            }
        });
        spyOn(api, 'save').and.returnValue($q.when({'user_preferences': update}));
    }));

    beforeEach(inject(function($injector, $q, session) {
        preferencesService = $injector.get('preferencesService');
        spyOn(session, 'getIdentity').and.returnValue($q.when({sessionId: 1}));
        session.sessionId = 1;
    }));

    it('can get user preferences', inject(function(api, $rootScope) {
        preferencesService.get();
        $rootScope.$digest();

        var preferences;
        preferencesService.get().then(function(_preferences) {
            preferences = _preferences;
        });

        $rootScope.$digest();

        expect(preferences).not.toBe(null);
        expect(preferences['archive:view'].view).toBe('mgrid');
        expect(api.find).toHaveBeenCalledWith('preferences', 1, null, true);
    }));

    it('can get user preferences by key', inject(function(api, $rootScope) {
        preferencesService.get();
        $rootScope.$digest();

        var preferences;
        preferencesService.get('archive:view').then(function(_preferences) {
            preferences = _preferences;
        });

        $rootScope.$digest();
        expect(preferences.view).toBe('mgrid');
    }));

    it('can get user preferences by key bypass the cache', inject(function(api, $rootScope) {
        var preferences;
        preferencesService.get('feature:preview', true).then(function(_preferences) {
            preferences = _preferences;
        });

        $rootScope.$digest();
        expect(preferences.enabled).toBe(false);
    }));

    it('update user preferences by key', inject(function(api, $q, $rootScope) {
        preferencesService.get();
        $rootScope.$digest();

        preferencesService.update(update, 'feature:preview');
        preferencesService.update({'workspace:active': {'workspace': ''}}, 'workspace:active');
        $rootScope.$digest();
        expect(api.save.calls.count()).toBe(1);

        var preferences;
        preferencesService.get('feature:preview').then(function(_preferences) {
            preferences = _preferences;
        });

        $rootScope.$digest();
        expect(preferences.enabled).toBe(false);
    }));

    it('can get all active privileges', inject(function(api, $rootScope) {
        preferencesService.get();
        $rootScope.$digest();

        var privileges;
        preferencesService.getPrivileges().then(function(_privileges) {
            privileges = _privileges;
        });

        $rootScope.$digest();
        expect(privileges.privilege1).toBe(1);
    }));

});

describe('preferences error handling', function() {

    beforeEach(module('superdesk.preferences'));
    beforeEach(module('superdesk.api'));

    beforeEach(inject(function(session, urls, $q, $httpBackend) {
        spyOn(session, 'getIdentity').and.returnValue($q.when());
        session.sessionId = 'sess1';
        spyOn(urls, 'resource').and.returnValue($q.when('/preferences'));
        $httpBackend.expectGET('/preferences/sess1').respond(404, {});
        $httpBackend.expectGET('/preferences/sess2').respond({});
    }));

    it('can reload on session expiry', inject(function(preferencesService, session, $rootScope, $httpBackend) {
        var success = jasmine.createSpy('success');
        var error = jasmine.createSpy('error');
        preferencesService.get().then(success, error);
        $rootScope.$digest();
        session.sessionId = 'sess2';
        $httpBackend.flush();
        expect(success).toHaveBeenCalled();
        expect(error).not.toHaveBeenCalled();
    }));
});
