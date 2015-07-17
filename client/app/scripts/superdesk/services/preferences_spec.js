define([
    './preferencesService',
    './storage'
], function(preferencesServiceSpec, storageSpec) {
    'use strict';

    describe('Preferences Service', function() {

        beforeEach(module(preferencesServiceSpec.name));
        beforeEach(module(storageSpec.name));
        beforeEach(module('superdesk.api'));

        var storage,
            preferencesService,
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
            spyOn(api, 'find').and.returnValue($q.when(testPreferences));
            spyOn(api, 'save').and.returnValue($q.when({'user_preferences': update}));
        }));

        beforeEach(inject(function($injector, $q, session, api) {
            storage = $injector.get('storage');
            preferencesService = $injector.get('preferencesService');
            storage.clear();

            spyOn(session, 'getIdentity').and.returnValue($q.when({sessionId: 1}));
        }));

        it('can get preferences', inject(function(api, $rootScope) {

            expect(storage.getItem('preferences')).toBe(null);
            $rootScope.sessionId = 1;
            preferencesService.get();

            $rootScope.$digest();
            var preferences = preferencesService.get();

            $rootScope.$digest();

            expect(preferences).not.toBe(null);
            expect(preferences).not.toBe(undefined);
            expect(storage.getItem('preferences')).not.toBe(null);
            expect(api.find).toHaveBeenCalledWith('preferences', 1, null, true);

        }));

        it('can get user preferences by key', inject(function(api, $rootScope) {

            expect(storage.getItem('preferences')).toBe(null);
            $rootScope.sessionId = 1;
            preferencesService.get();

            $rootScope.$digest();
            var preferences;
            preferencesService.get('archive:view').then(function(_preferences) {
                preferences = _preferences;
            });

            $rootScope.$digest();

            expect(preferences.view).toBe('mgrid');
            expect(storage.getItem('preferences')).not.toBe(null);

        }));

        it('update user preferences by key', inject(function(api, $q, $rootScope) {
            expect(storage.getItem('preferences')).toBe(null);
            $rootScope.sessionId = 1;
            preferencesService.get();
            $rootScope.$digest();

            preferencesService.update(update, 'feature:preview');
            preferencesService.update({'workspace:active': {'workspace': ''}}, 'workspace:active');
            $rootScope.$digest();
            expect(api.save.calls.count()).toBe(1);

            expect(storage.getItem('preferences').user_preferences['feature:preview'].enabled).toBe(false);
        }));

        it('can remove preferences', inject(function(api, $rootScope) {

            expect(storage.getItem('preferences')).toBe(null);
            $rootScope.sessionId = 1;
            preferencesService.get();

            $rootScope.$digest();

            var preferences = preferencesService.get('archive:view');
            expect(preferences).not.toBe(null);
            expect(storage.getItem('preferences')).not.toBe(null);

            preferencesService.remove();

            expect(storage.getItem('preferences')).toBe(null);

        }));

        it('can get all active privileges', inject(function(api, $rootScope) {

            expect(storage.getItem('preferences')).toBe(null);
            $rootScope.sessionId = 1;
            preferencesService.get();

            $rootScope.$digest();
            preferencesService.getPrivileges();

            $rootScope.$digest();

            expect(storage.getItem('preferences').active_privileges.privilege1).toBe(1);

        }));
    });
});
