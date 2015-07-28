'use strict';

describe('content', function() {
    var item = {_id: 1};

    beforeEach(module('templates'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive'));
    beforeEach(module('superdesk.workspace.content'));

    it('can spike items', inject(function(spike, api, $q) {
        spyOn(api, 'update').and.returnValue($q.when());
        spike.spike(item);
        expect(api.update).toHaveBeenCalledWith('archive_spike', item, {state: 'spiked'});
    }));

    it('can unspike items', inject(function(spike, api, $q) {
        spyOn(api, 'update').and.returnValue($q.when());
        spike.unspike(item);
        expect(api.update).toHaveBeenCalledWith('archive_unspike', item, {});
    }));

    describe('multi service', function() {
        it('can reset on route change', inject(function(multi, $rootScope) {
            multi.toggle({_id: 1, selected: true});
            expect(multi.count).toBe(1);
            expect(multi.getIds()).toEqual([1]);

            $rootScope.$broadcast('$routeChangeStart');
            $rootScope.$digest();

            expect(multi.count).toBe(0);
        }));

        it('can get list of items', inject(function(multi) {
            var items = [{_id: 1, selected: true}, {_id: 2, selected: true}];
            multi.toggle(items[0]);
            multi.toggle(items[1]);
            expect(multi.getItems()).toEqual(items);
        }));
    });

    describe('media box directive', function() {
        it('can select item for multi editing', inject(function(multi, $rootScope, $compile) {
            var scope = $rootScope.$new();
            scope.item = {_id: 1};

            $compile('<div sd-media-box></div>')(scope);
            scope.$digest();

            expect(multi.getItems().length).toBe(0);
            scope.item.selected = true;
            scope.toggleSelected(scope.item);
            expect(multi.getItems().length).toBe(1);

            multi.reset();
            $rootScope.$digest();
            expect(multi.getItems().length).toBe(0);
        }));
    });

    describe('creating items', function() {
        beforeEach(module(function($provide) {
            $provide.service('api', function($q) {
                return function() {
                    return {
                        save: function() {
                            return $q.when();
                        }
                    };
                };
            });
        }));

        it('can create plain text items', inject(function(superdesk, $rootScope, ContentCtrl) {
            spyOn(superdesk, 'intent').and.returnValue(null);

            var content = new ContentCtrl();
            content.createItem();
            $rootScope.$digest();
            expect(superdesk.intent).toHaveBeenCalledWith('author', 'article', {type: 'text', version: 0});
        }));

        it('can create packages', inject(function(superdesk, ContentCtrl) {
            spyOn(superdesk, 'intent').and.returnValue(null);

            var content = new ContentCtrl();
            content.createPackageItem();
            expect(superdesk.intent).toHaveBeenCalledWith('create', 'package');
        }));

        it('can create packages from items', inject(function(superdesk, ContentCtrl) {
            spyOn(superdesk, 'intent').and.returnValue(null);

            var content = new ContentCtrl();
            content.createPackageItem({data: 123});
            expect(superdesk.intent).toHaveBeenCalledWith('create', 'package', {items: [{data: 123}]});
        }));

        it('can create items from template', inject(function(superdesk, $rootScope, ContentCtrl) {
            spyOn(superdesk, 'intent').and.returnValue(null);

            var content = new ContentCtrl();
            content.createFromTemplateItem({
                slugline: 'test_slugline',
                body_html: 'test_body_html',
                irrelevantData: 'yes'
            });
            $rootScope.$digest();
            expect(superdesk.intent).toHaveBeenCalledWith('author', 'article', {
                slugline: 'test_slugline',
                body_html: 'test_body_html'
            });
        }));

    });
});
