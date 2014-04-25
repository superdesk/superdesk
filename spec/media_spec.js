
var openUrl = require('./utils').open;

describe('Media Archive', function() {
    'use strict';

    describe('list', function() {

        beforeEach(openUrl('/#/media'));

        xit('should display list of media items', function() {
            expect(element.all(by.repeater('items')).count()).toBe(0);
        });
    });
});
