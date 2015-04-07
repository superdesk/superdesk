
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring');

describe('multi content widget', function() {
    it('can show items grouped by stage', function() {
        workspace.open();
        workspace.editItem(1);
        authoring.sendTo('Sports Desk');
        workspace.editItem(0, 'SPORTS DESK');

        // only now play with widget
        element(by.id('Aggregate')).click();
        // here the math is tricky, because you get here also stages without content that are not visible..
        var stage = element.all(by.repeater('stage in deskStages')).get(4);
        expect(stage.element(by.css('.stage-header')).getText())
            .toBe('SPORTS DESK : NEW\n1');
        expect(stage.all(by.repeater('item in items')).first().element(by.css('.text')).getText())
            .toBe('item1');
    });

    it('can open item stage', function() {
        workspace.open();
        workspace.editItem(0, 'SPORTS DESK');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content$/);
    });
});
