'use strict';

describe('highlights', function() {

    beforeEach(module('superdesk.highlights'));
    beforeEach(module('templates'));
    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive'));

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

});
