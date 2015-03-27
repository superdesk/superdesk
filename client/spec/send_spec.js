
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring');

describe('Send To', function() {
    it('can submit item to a desk', function() {
        workspace.open();
        workspace.editItem(1);
        authoring.sendTo('Sports Desk');
        workspace.switchToDesk('SPORTS DESK');
        expect(
            element.all(by.repeater('items._items'))
                .first()
                .element(by.css('.state-label'))
                .getText()
        ).toBe('SUBMITTED');
    });
});
