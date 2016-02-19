
'use strict';

describe('superdesk.workspace.content', function() {

    beforeEach(module('templates'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.desks'));
    beforeEach(module('superdesk.workspace.content'));

    describe('content service', function() {
        var done;
        var ITEM = {};

        beforeEach(inject(function(api, $q) {
            spyOn(api, 'save').and.returnValue($q.when(ITEM));
            done = jasmine.createSpy('done');
        }));

        it('can create plain text items', inject(function(api, content, $rootScope) {
            content.createItem().then(done);
            $rootScope.$digest();
            expect(api.save).toHaveBeenCalledWith('archive', {type: 'text', version: 0});
            expect(done).toHaveBeenCalledWith(ITEM);
        }));

        it('can create packages', inject(function(api, content, $rootScope) {
            content.createPackageItem().then(done);
            $rootScope.$digest();
            expect(api.save).toHaveBeenCalledWith('archive', {headline: '', slugline: '',
                description_text: '', type: 'composite',
                groups: [{role: 'grpRole:NEP', refs: [{idRef: 'main'}], id: 'root'},
                {refs: [], id: 'main', role: 'grpRole:main'}], version: 0});
            expect(done).toHaveBeenCalledWith(ITEM);
        }));

        it('can create packages from items', inject(function(api, content, $rootScope) {
            content.createPackageItem({data: 123}).then(done);
            $rootScope.$digest();
            expect(done).toHaveBeenCalledWith(ITEM);
        }));

        it('can create items from template', inject(function(api, content, $rootScope) {
            content.createItemFromTemplate({
                slugline: 'test_slugline',
                body_html: 'test_body_html',
                irrelevantData: 'yes'
            }).then(done);
            $rootScope.$digest();
            expect(done).toHaveBeenCalledWith(ITEM);
            expect(api.save).toHaveBeenCalledWith('archive', {
                slugline: 'test_slugline',
                body_html: 'test_body_html'
            });
        }));

        it('can fetch content types', inject(function(api, content, $rootScope, $q) {
            var types = [{_id: 'foo'}];
            spyOn(api, 'query').and.returnValue($q.when({_items: types}));
            var success = jasmine.createSpy('ok');
            content.getTypes().then(success);
            $rootScope.$digest();
            expect(api.query).toHaveBeenCalledWith('content_types', {where: {enabled: true}});
            expect(success).toHaveBeenCalledWith(types);
            expect(content.types).toBe(types);
        }));

        it('can get content type', inject(function(api, content, $rootScope, $q) {
            var type = {_id: 'foo'};
            spyOn(api, 'find').and.returnValue($q.when(type));
            var success = jasmine.createSpy('ok');
            content.getType('foo').then(success);
            $rootScope.$digest();
            expect(api.find).toHaveBeenCalledWith('content_types', 'foo');
            expect(success).toHaveBeenCalledWith(type);
        }));

        it('can create item using content type', inject(function(api, content, desks, session) {
            var type = {_id: 'test'};
            var success = jasmine.createSpy('ok');
            desks.activeDeskId = 'sports';
            desks.userDesks = {_items: [{_id: 'sports', working_stage: 'inbox'}]};
            session.identity = {_id: 'foo'};
            content.createItemFromContentType(type).then(success);
            expect(api.save).toHaveBeenCalledWith('archive', {
                profile: type._id,
                type: 'text',
                version: 0,
                task: {desk: 'sports', stage: 'inbox', user: 'foo'}
            });
        }));
    });
});
