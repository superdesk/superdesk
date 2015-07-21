'use strict';

describe('legal archive service', function() {
    beforeEach(module('superdesk.api'));
    beforeEach(module('superdesk.legal_archive'));

    it('can create base query', inject(function(legal) {
        var criteria = legal.getCriteria();
        expect(criteria.sort).toEqual('[("versioncreated", -1)]');
        expect(criteria.max_results).toBe(25);
    }));

    it('can create query string query', inject(function($rootScope, legal) {
        legal.updateSearchQuery({_id: '123'});
        $rootScope.$digest();
        var criteria = legal.getCriteria();
        expect(criteria.where).toBe('{"_id":{"$regex":"123","$options":"-i"}}');

        legal.updateSearchQuery({headline: 'test'});
        $rootScope.$digest();
        criteria = legal.getCriteria();
        expect(criteria.where).toBe('{"headline":{"$regex":"test","$options":"-i"}}');

        legal.updateSearchQuery({_id: '123', headline: 'test'});
        $rootScope.$digest();
        criteria = legal.getCriteria();
        expect(criteria.where).toBe(angular.toJson({$and: [
            {_id: {$regex: '123', $options: '-i'}},
            {headline: {$regex: 'test', $options: '-i'}}
        ]}));

        legal.updateSearchQuery({published_after: '2015-06-16T14:00:00+00:00'});
        $rootScope.$digest();
        criteria = legal.getCriteria();
        expect(criteria.where).toBe('{"versioncreated":{"$gte":"2015-06-16T14:00:00+0000"}}');

        legal.updateSearchQuery({published_before: '2015-05-16T14:00:00+00:00'});
        $rootScope.$digest();
        criteria = legal.getCriteria();
        expect(criteria.where).toBe('{"versioncreated":{"$lte":"2015-05-16T14:00:00+0000"}}');

        legal.updateSearchQuery({_id: '123', headline: 'test', published_after: '2015-06-16T14:00:00+00:00'});
        $rootScope.$digest();
        criteria = legal.getCriteria();
        /*jshint multistr: true */
        expect(criteria.where).toBe('{"$and":[' + [
            '{"_id":{"$regex":"123","$options":"-i"}}',
            '{"headline":{"$regex":"test","$options":"-i"}}',
            '{"versioncreated":{"$gte":"2015-06-16T14:00:00+0000"}}'
        ].join(',') + ']}');
    }));

    it('can sort items', inject(function(legal, $location, $rootScope) {
        legal.setSort('urgency');
        $rootScope.$digest();
        expect($location.search().sort).toBe('urgency:desc');
        expect(legal.getSort()).toEqual({label: 'News Value', field: 'urgency', dir: 'desc'});

        legal.toggleSortDir();
        $rootScope.$digest();
        expect(legal.getSort()).toEqual({label: 'News Value', field: 'urgency', dir: 'asc'});
    }));

});
