define([
    'superdesk/directives/listView',
    'superdesk/services/keyboardManager',
    'angular-mocks'
], function(ListViewModule, kbModule) {
    'use strict';

    describe('ListView directive', function() {
        var $compile, $rootScope;

        beforeEach(module(ListViewModule.name));
        beforeEach(module(kbModule.name));
        beforeEach(module('templates'));
        beforeEach(module('ngMock'));

        beforeEach(inject(function($injector) {
            $compile = $injector.get('$compile');
            $rootScope = $injector.get('$rootScope');
        }));

        it('renders list', function() {
            $rootScope.adapter = {
                collection: [{href: 1, name: 'foo'}, {href: 2, name: 'bar'}]
            };

            var elem = $compile('<div sd-list-view data-adapter="adapter"><div class="item">{{ item.name }}</div></div>')($rootScope);
            $rootScope.$digest();

            expect(elem.html()).toContain('foo');
            expect(elem.find('.item').length).toBe(2);
        });
    });
});
