
var openUrl = require('./utils').open;

describe('Media Archive', function() {
    'use strict';

    describe('archive', function() {

        beforeEach(openUrl('/#/archive/'));

        it('should display list of media items', function() {
            expect(element.all(by.repeater('item in items')).count()).toBe(3);
        });
    });
});
