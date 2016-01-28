'use strict';

describe('Tag Service', function() {

    var deskList = {
        desk1: {id: '123', title: 'desk1'},
        desk2: {id: '456', title: 'desk2'}
    };

    var fakeMetadata;

    beforeEach(module('superdesk.search'));
    beforeEach(module('superdesk.desks'));
    beforeEach(module('superdesk.templates-cache'));

    /**
     * Mock some of the dependencies of the parent directives.
     */
    beforeEach(module(function ($provide) {
        fakeMetadata = {
            values: {subjectcodes: []},
            fetchSubjectcodes: jasmine.createSpy()
        };

        $provide.value('metadata', fakeMetadata);
    }));

    beforeEach(inject(function($q) {
        fakeMetadata.fetchSubjectcodes.and.returnValue($q.when());
    }));

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
        expect(members.selectedKeywords.length).toBe(2);
        expect(members.selectedParameters.length).toBe(1);

    }));

    it('create tags for from desk and to desk', inject(function ($location, $rootScope, $q, tags, _desks_) {
        var desks = _desks_;
        desks.deskLookup = {
            from: {
                name: 'National'
            },
            to: {
                name: 'Sport'
            }
        };

        $location.search('from_desk', 'from-authoring');
        $location.search('to_desk', 'to-authoring');

        spyOn(desks, 'initialize').and.returnValue($q.when([]));

        var tagsList = null;
        tags.initSelectedFacets()
            .then(function(value) {
                tagsList = value;
            });

        $rootScope.$digest();
        expect(tagsList.selectedParameters.length).toEqual(2);
        expect(tagsList.selectedParameters[0]).toEqual('From Desk:National');
        expect(tagsList.selectedParameters[1]).toEqual('To Desk:Sport');
    }));

    it('create tags original creator', inject(function ($location, $rootScope, $q, tags, desks, _userList_) {
        var userList = _userList_;

        $location.search('original_creator', '123');

        var user = {
            _id: '123',
            display_name: 'Test User'
        };

        spyOn(userList, 'getUser').and.returnValue($q.when(user));
        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        var tagsList = null;
        tags.initSelectedFacets()
            .then(function(value) {
                tagsList = value;
            });

        $rootScope.$digest();
        expect(tagsList.selectedParameters.length).toEqual(1);
        expect(tagsList.selectedParameters[0]).toEqual('Creator:Test User');
    }));

    it('create tags if creator is not known', inject(function ($location, $rootScope, $q, tags, desks, _userList_) {
        var userList = _userList_;

        $location.search('original_creator', '123');

        spyOn(userList, 'getUser').and.returnValue($q.reject({}));
        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        var tagsList = null;
        tags.initSelectedFacets()
            .then(function(value) {
                tagsList = value;
            });

        $rootScope.$digest();
        expect(tagsList.selectedParameters.length).toEqual(1);
        expect(tagsList.selectedParameters[0]).toEqual('Creator:Unknown');
    }));

    it('create tags for unique name', inject(function ($location, $rootScope, $q, tags, desks) {
        $location.search('unique_name', '123');

        spyOn(desks, 'initialize').and.returnValue($q.when({deskLookup: deskList}));

        var tagsList = null;
        tags.initSelectedFacets()
            .then(function(value) {
                tagsList = value;
            });

        $rootScope.$digest();
        expect(tagsList.selectedParameters.length).toEqual(1);
        expect(tagsList.selectedParameters[0]).toEqual('Unique Name:123');
    }));
});
