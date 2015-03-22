
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Send To', function() {

    beforeEach(function(done) {openUrl('/#/workspace/content').then(done);});

    it('can submit item to a desk', function() {
        var sidebar;
        workspace.switchToDesk('PERSONAL').then(
            content.setListView
        ).then(function() {
            return content.actionOnItem('Edit item', 1);
        }).then(function() {
            return element(by.id('send-to-btn')).click();
        }).then(function() {
            // send to sports
            sidebar = element(by.css('.send-to-pane'));
            return sidebar.element(by.css('.desk-select .dropdown-toggle'))
                .waitReady();
        }).then(function(elem) {
            return elem.click();
        }).then(function() {
            return sidebar.element(by.buttonText('Sports Desk')).click();
        }).then(function() {
            return sidebar.element(by.buttonText('send')).click();
        }).then(function() {
            return workspace.switchToDesk('SPORTS DESK');
        });
        expect(
            element.all(by.repeater('items._items'))
                .first()
                .element(by.css('.state-label'))
                .getText()
        ).toBe('SUBMITTED');
    });
});
