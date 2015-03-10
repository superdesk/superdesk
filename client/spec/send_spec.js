
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
	content = require('./helpers/pages').content;

describe('Send To', function() {

    beforeEach(openUrl('/#/workspace/content'));

    it('can submit item to a desk', function() {
        workspace.switchToDesk('PERSONAL');
        element.all(by.repeater('items._items')).first().click();
        content.actionOnItem('Edit item', 1);
        element(by.id('send-to-btn')).click();
        browser.sleep(200);

        // send to sports
        var sidebar = element(by.css('.send-to-pane'));
        sidebar.element(by.css('.desk-select .dropdown-toggle')).click();
        sidebar.element(by.buttonText('Sports Desk')).click();
        sidebar.element(by.buttonText('send')).click();

        workspace.switchToDesk('SPORTS DESK');
        expect(element.all(by.repeater('items._items')).first().element(by.css('.state-label')).getText())
            .toBe('SUBMITTED');
    });
});
