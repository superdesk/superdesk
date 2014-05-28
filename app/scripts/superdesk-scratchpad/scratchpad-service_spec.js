define([
    'superdesk/services/storage',
    './scratchpad-service'
], function(storageService, ScratchpadService) {
    'use strict';

    describe('scratchpadService', function() {
        beforeEach(function() {
            module(storageService.name);
            module(function($provide) {
                $provide.service('scratchpad', ScratchpadService);
            });
        });

        var $q, storage, service, testItem, testItem2;

        beforeEach(module(function($provide) {
            $provide.service('api', function($q) {
                return {
                    archive: {
                        getByUrl: function() {
                            return $q.when(testItem);
                        },
                        getHeaders: function() {
                            return {};
                        }
                    }
                };
            });
        }));

        beforeEach(inject(function($injector) {
            $q = $injector.get('$q');
            storage = $injector.get('storage');
            service = $injector.get('scratchpad');
            testItem = {
                _links: {self: {href: 'test'}},
                data: 1
            };
            testItem2 = {
                _links: {self: {href: 'test2'}},
                data: 2
            };
            storage.clear();
            service.itemList = [];
            service.data = {};
        }));

        it('can add items', function() {
            service.addItem(testItem);
            var item = storage.getItem('scratchpad:items');
            expect(item).toEqual(['test']);
        });

        it('can remove items', function() {
            service.addItem(testItem);
            service.removeItem(testItem);
            var item = storage.getItem('scratchpad:items');
            expect(item).toEqual([]);
        });

        it('can check if item exists and return false', function() {
            var test = service.checkItemExists(testItem);
            expect(test).toEqual(false);
        });

        it('can check if item exists and return true', function() {
            service.addItem(testItem);
            var test = service.checkItemExists(testItem);
            expect(test).toEqual(true);
        });

        it('can sort items', function() {
            service.addItem(testItem);
            service.addItem(testItem2);
            service.sort([1, 0]);
            var test = storage.getItem('scratchpad:items');
            expect(test).toEqual(['test2', 'test']);
        });

        it('can get items', inject(function($rootScope) {
            var test = null;

            service.addItem(testItem);
            service.data = {};

            service.getItems().then(function(response) {
                test = response[0];
            });

            $rootScope.$apply();

            expect(test.data).toEqual(testItem.data);
        }));

        it('can announce to listeners', function() {
            var test = false;

            service.addListener(function() {
                test = true;
            });

            expect(test).toEqual(false);

            service.addItem(testItem);

            expect(test).toEqual(true);
        });
    });
});
