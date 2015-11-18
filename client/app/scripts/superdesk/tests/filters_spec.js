'use strict';

describe('superdesk filters', function() {
    beforeEach(module('superdesk.filters'));

    describe('sort items', function() {

        it('can ignore case while sorting', inject(function(sortByNameFilter) {
            var unorderedList = [{name: 'c'}, {name: 'A'}, {name: 'b'}];

            expect(sortByNameFilter(unorderedList)).toEqual([{name: 'A'}, {name: 'b'}, {name: 'c'}]);
        }));

        it('can sort on a different property and ignore case while sorting', inject(function(sortByNameFilter) {
            var unorderedList = [{name: 'c', display_name: 'category'}, {name: 'A', display_name: 'ANPA Categories'},
                                 {name: 'b', display_name: 'broadcast'}];

            expect(sortByNameFilter(unorderedList, 'display_name')).toEqual([
                {name: 'A', display_name: 'ANPA Categories'}, {name: 'b', display_name: 'broadcast'},
                {name: 'c', display_name: 'category'}]);
        }));

    });

});
