'use strict';

describe('Tag Service', function() {

    var deskList = {
        desk1: {id: '123', title: 'desk1'},
        desk2: {id: '456', title: 'desk2'}
    };

    beforeEach(module('superdesk.search'));
    beforeEach(module('superdesk.desks'));

    it('can populate keywords from location', inject(function($location, tags, $rootScope, desks, $q) {
        var members = null;
        $location.search('q=(Obama)');
        $rootScope.$apply();

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        tags.initSelectedFacets()
            .then(function(currentTags) {
                members = currentTags;
            });

        $rootScope.$digest();
        expect(members.selectedKeywords.length).toBe(1);
    }));

    it('can populate parameters from location', inject(function($location, tags, $rootScope, desks, $q) {
        var members = null;
        $location.search('q=headline:(Obama)');
        $rootScope.$apply();

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        tags.initSelectedFacets()
            .then(function(currentTags) {
                members = currentTags;
            });

        $rootScope.$digest();
        expect(members.selectedParameters.length).toBe(1);
    }));

    it('can populate type facet from location', inject(function($location, tags, $rootScope, desks, $q) {
        var members = null;
        $location.search('type=["text"]');
        $rootScope.$apply();

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        tags.initSelectedFacets()
            .then(function(currentTags) {
                members = currentTags;
            });

        $rootScope.$digest();
        expect(members.selectedFacets.type.length).toBe(1);
    }));

    it('can populate date facet from location', inject(function($location, tags, $rootScope, desks, $q) {
        var members = null;
        $location.search('after=now-1M');
        $rootScope.$apply();

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        tags.initSelectedFacets()
            .then(function(currentTags) {
                members = currentTags;
            });

        $rootScope.$digest();
        expect(members.selectedFacets.date.length).toBe(1);
        expect(members.selectedFacets.date[0]).toBe('Last Month');
    }));

    it('can populate complete filters from location', inject(function($location, tags, $rootScope, desks, $q) {
        var members = null;
        $location.search([
            'type=["text","composite"]',
            'state=["submitted","faked","madeup"]',
            'q=slugline:(FBI) (Obama) (Australia)'
        ].join('&'));
        $rootScope.$apply();

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        tags.initSelectedFacets()
            .then(function(currentTags) {
                members = currentTags;
            });

        $rootScope.$digest();
        expect(members.selectedFacets.type.length).toBe(2);
        expect(members.selectedFacets.state.length).toBe(3);
        expect(members.selectedKeywords.length).toBe(2);
        expect(members.selectedParameters.length).toBe(1);

    }));
});
