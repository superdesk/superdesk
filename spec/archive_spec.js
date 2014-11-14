
var openUrl = require('./helpers/utils').open;

describe('Media Archive', function() {
    'use strict';

    describe('archive', function() {

        beforeEach(openUrl('/#/workspace/content'));

        xit('should display list of media items', function() {
            element(by.binding('selectedDesk')).click();
            element(by.repeater('desk in desks').row(1)).click();
            expect(element.all(by.repeater('item in items')).count()).toBe(3);
        });
    });
});
