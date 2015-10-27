'use strict';

describe('content', function() {
    var item = {_id: 1};

    beforeEach(module('superdesk.templates-cache'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive'));

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

    describe('archive service', function() {
        beforeEach(inject(function (desks, session) {
            session.identity = {_id: 'user:1'};

            desks.userDesks = {_items: [{_id: '1', name: 'sport', incoming_stage: '2'},
                                        {_id: '2', name: 'news', incoming_stage: '1'}]};
            desks.setCurrentDeskId('2');

            item = {'_id': '123'};
        }));

        it('can add an item to a desk', inject(function(archiveService) {
            archiveService.addTaskToArticle(item);

            expect(item.task.desk).toBe('2');
            expect(item.task.stage).toBe('1');
        }));

        it('verifies if item is from Legal Archive or not', inject(function(archiveService) {
            expect(archiveService.isLegal(item)).toBe(false);

            item._type = 'legal_archive';
            expect(archiveService.isLegal(item)).toBe(true);
        }));

        it('returns the related items', inject(function(archiveService, api, $q, search) {
            spyOn(api, 'query').and.returnValue($q.when());
            archiveService.getRelatedItems('test');
            expect(api.query).toHaveBeenCalled();
            var criteria = api.query.calls.mostRecent().args[1];
            expect(criteria.source.query.filtered.query.query_string.query).toBe('slugline:(test)');
        }));

        it('can verify if the item is published or not', inject(function(archiveService) {
            item.state = 'submitted';
            expect(archiveService.isPublished(item)).toBe(false);

            item.state = 'corrected';
            expect(archiveService.isPublished(item)).toBe(true);
        }));

        it('return type based on state and repository', inject(function(archiveService) {
            item.state = 'spiked';
            expect(archiveService.getType(item)).toBe('spike');

            item.state = 'ingested';
            expect(archiveService.getType(item)).toBe('ingest');

            item.state = 'submitted';
            expect(archiveService.getType(item)).toBe('archive');

            item.state = 'published';
            item.allow_post_publish_actions = true;
            expect(archiveService.getType(item)).toBe('archive');

            item.allow_post_publish_actions = false;
            expect(archiveService.getType(item)).toBe('archived');

            item._type = 'legal_archive';
            expect(archiveService.getType(item)).toBe('legal_archive');

            item._type = 'externalsource';
            expect(archiveService.getType(item)).toBe('externalsource');
        }));

        it('can fetch version history', inject(function(archiveService, api, $q) {
            spyOn(api, 'find').and.returnValue($q.when());
            spyOn(api.legal_archive_versions, 'getByUrl').and.returnValue($q.when());

            item._links = {_id: '123'};
            archiveService.getVersionHistory(item, {}, 'versions');
            expect(api.find).toHaveBeenCalledWith('archive', '123', {version: 'all', embedded: {user: 1}});

            item._type = 'legal_archive';
            item._links = {collection: {href: '/legal_archive'}};
            archiveService.getVersionHistory(item, {}, 'versions');
            expect(api.find).toHaveBeenCalledWith('legal_archive', '123', {version: 'all'});
        }));
    });

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
    describe('media-related directive', function() {
        it('can view item', inject(function(familyService, $rootScope, $compile, superdesk, $q) {
            var scope = $rootScope.$new();
            scope.item = {_id: 1, family_id: 1};

            var elem = $compile('<div sd-media-related data-item=\'item\'></div>')(scope);
            scope.$digest();

            var iscope = elem.isolateScope();
            expect(iscope.item).toBe(scope.item);

            scope.relatedItems = {_items: [{_id: 2, family_id: 1}]};

            spyOn(superdesk, 'intent').and.returnValue($q.when());
            iscope.open(scope.relatedItems._items[0]);
            scope.$apply();

            expect(superdesk.intent).toHaveBeenCalledWith('view', 'item', scope.relatedItems._items[0]);
        }));
        it('can fetch related items when item duplicated',
            inject(function(familyService, $rootScope, $compile, superdesk, $q) {
            var scope = $rootScope.$new();
            scope.item = {_id: 1, family_id: 1};

            var elem = $compile('<div sd-media-related data-item=\'item\'></div>')(scope);
            scope.$digest();

            var iscope = elem.isolateScope();
            expect(iscope.item).toBe(scope.item);

            spyOn(familyService, 'fetchItems').and.returnValue($q.when());
            scope.$broadcast('item:duplicate');
            scope.$apply();

            expect(familyService.fetchItems).toHaveBeenCalledWith(scope.item.family_id, scope.item);
        }));
    });

    describe('item preview container', function() {
        it('can handle preview:item intent', inject(function($rootScope, $compile, superdesk) {
            var scope = $rootScope.$new();
            var elem = $compile('<div sd-item-preview-container></div>')(scope);
            scope.$digest();

            var iscope = elem.isolateScope();
            expect(iscope.item).toBe(null);

            scope.$apply(function() {
                superdesk.intent('preview', 'item', item);
            });

            expect(iscope.item).toBe(item);

            iscope.close();
            expect(iscope.item).toBe(null);
        }));
    });
});
