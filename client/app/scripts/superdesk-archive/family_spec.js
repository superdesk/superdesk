'use strict';

describe('familyService', function() {
    var items = [
        {_id: 'z', family_id: 'family1', task: {desk: 'desk1'}},
        {_id: 'x', family_id: 'family1', task: {desk: 'desk2'}},
        {_id: 'c', family_id: 'family2', task: {desk: 'desk3'}}
    ];
    var deskList = {
        desk1: {title: 'desk1'},
        desk3: {title: 'desk3'}
    };

    beforeEach(module('superdesk.mocks'));
    beforeEach(module('superdesk.archive.directives'));
    beforeEach(module('templates'));

    beforeEach(module(function($provide) {
        $provide.service('api', function($q) {
            return function() {
                return {
                    find: function() {
                        return $q.reject({});
                    },
                    query: function(params) {
                        var familyId = params.source.query.filtered.filter.and[1].term.family_id;
                        var members = _.filter(items, {family_id: familyId});

                        if (params.source.query.filtered.filter.and[2]) {
                            _.remove(members, {_id: params.source.query.filtered.filter.and[2].not.term._id});
                        }

                        return $q.when({_items: members});
                    }
                };
            };
        });
        $provide.service('desks', function() {
            return {
                deskLookup: deskList
            };
        });
    }));

    it('can fetch members of a family', inject(function($rootScope, familyService, api) {
        var members = null;
        familyService.fetchItems('family1')
        .then(function(result) {
            members = result;
        });
        $rootScope.$digest();
        expect(members._items.length).toBe(2);
    }));

    it('can fetch members of a family with exclusion', inject(function($rootScope, familyService, api) {
        var members = null;
        familyService.fetchItems('family1', {_id: 'z'})
        .then(function(result) {
            members = result;
        });
        $rootScope.$digest();
        expect(members._items.length).toBe(1);
    }));

    it('can fetch desks of members of a family', inject(function($rootScope, familyService, api, desks) {
        var memberDesks = null;
        familyService.fetchDesks({_id: 'z', family_id: 'family1'})
        .then(function(result) {
            memberDesks = result;
        });
        $rootScope.$digest();
        expect(memberDesks.length).toBe(1);
    }));

    it('can fetch desks of members of a family with exclusion',
    inject(function($rootScope, familyService, api, desks) {
        var memberDesks = null;
        familyService.fetchDesks({_id: 'z', family_id: 'family1'}, true)
        .then(function(result) {
            memberDesks = result;
        });
        $rootScope.$digest();
        expect(memberDesks.length).toBe(0);
    }));

    it('can use item._id for ingest items instead of family id',
    inject(function($rootScope, $q, familyService) {
        spyOn(familyService, 'fetchItems').and.returnValue($q.when({}));
        familyService.fetchDesks({_id: 'id', family_id: 'family_id', state: 'ingested'});
        expect(familyService.fetchItems).toHaveBeenCalledWith('id', undefined);
    }));
});
