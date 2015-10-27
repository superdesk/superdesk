'use strict';

describe('highlights', function() {

    beforeEach(module('superdesk.highlights'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive'));
    beforeEach(module('superdesk.templates-cache'));

    describe('sdPackageHighlightsDropdown directive', function() {
        var scope, desk;

        beforeEach(inject(function (desks, highlightsService, $rootScope, $compile, $q) {
            desk = {_id: '123'};
            desks.setCurrentDeskId(desk._id);

            spyOn(highlightsService, 'get').and.returnValue($q.when({_items: [
                {_id: '1', name: 'Spotlight'},
                {_id: '2', name: 'New'}
            ]}));

            scope = $rootScope.$new();
            $compile('<div dropdown sd-package-highlights-dropdown></div>')(scope);
            scope.$digest();
        }));

        it('can set highlights', inject(function (desks, highlightsService, $q, $rootScope) {
            var active = desks.active;
            expect(active.desk).toEqual('123');
            $rootScope.$digest();
            expect(highlightsService.get).toHaveBeenCalledWith(active.desk);
        }));
    });

    describe('create highlights button directive', function() {
        it('can create highlights package',
        inject(function($compile, $rootScope, $q, api, authoringWorkspace, authoring) {
            var scope = $rootScope.$new();
            var elem = $compile('<div sd-create-highlights-button highlight="\'foo\'"></div>')(scope);
            scope.$digest();
            var iscope = elem.isolateScope();

            var highlight = {_id: 'foo_highlight', name: 'Foo'};
            var pkg = {_id: 'foo_package'};
            spyOn(api, 'find').and.returnValue($q.when(highlight));
            spyOn(api, 'save').and.returnValue($q.when(pkg));
            spyOn(authoring, 'open').and.returnValue($q.when(pkg));

            iscope.createHighlight();
            $rootScope.$digest();
            expect(api.find).toHaveBeenCalledWith('highlights', 'foo');
            expect(api.save).toHaveBeenCalledWith('archive',
                jasmine.objectContaining({headline: 'Foo', highlight: 'foo_highlight'}));
        }));
    });
});
