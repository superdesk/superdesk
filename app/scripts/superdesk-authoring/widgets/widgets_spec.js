
'use strict';

describe('authoring widgets', function() {

    beforeEach(module('templates'));

    angular.module('superdesk.authoring.widgets.test', ['superdesk.authoring.widgets'])
        .config(function(authoringWidgetsProvider) {
            authoringWidgetsProvider.widget('test', {});
        });

    beforeEach(module('superdesk.authoring.widgets.test'));

    it('can register authoring widgets', inject(function(authoringWidgets) {
        expect(authoringWidgets.length).toBe(1);
    }));
});
