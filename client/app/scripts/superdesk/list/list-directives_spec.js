'use strict';

describe('list directives', function() {
    beforeEach(module('superdesk.list'));
    beforeEach(module('templates'));

    it('renders list', inject(function($compile, $rootScope) {
        var scope = $rootScope.$new(true);
        scope.items = [{href: 1, name: 'foo'}, {href: 2, name: 'bar'}];

        var elem = $compile('<div sd-list-view data-items="items">' +
            '<div class="item">{{ item.name }}</div></div>')(scope);
        scope.$digest();

        expect(elem.html()).toContain('foo');
        expect(elem.find('.item').length).toBe(2);
    }));

    it('renders searchbar', inject(function($compile, $location, $rootScope) {
        var scope = $rootScope.$new(true);
        var elem = $compile('<div sd-searchbar></div>')(scope);
        $location.search('page', 1);
        scope.$digest();

        var iscope = elem.scope();
        iscope.q = 'test';
        iscope.search();
        iscope.$digest();

        expect($location.search().q).toBe('test');
        expect($location.search().page).toBe(undefined);
    }));
});
