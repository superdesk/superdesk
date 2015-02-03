define([
    './list',
    '../services/keyboardManager',
    './views/list-view.html'
], function(ListModule, kbModule) {
    'use strict';

    describe('ListView directive', function() {
        beforeEach(module(ListModule.name));
        beforeEach(module(kbModule.name));
        beforeEach(module('templates'));

        it('renders list', inject(function($compile, $rootScope) {
            var scope = $rootScope.$new(true);
            scope.items = [{href: 1, name: 'foo'}, {href: 2, name: 'bar'}];

            var elem = $compile('<div sd-list-view data-items="items"><div class="item">{{ item.name }}</div></div>')(scope);
            scope.$digest();

            expect(elem.html()).toContain('foo');
            expect(elem.find('.item').length).toBe(2);
        }));
    });
});
