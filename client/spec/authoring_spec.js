
'use strict';

var workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring');

describe('authoring', function() {
    it('can open item stage', function() {
        workspace.open();
        workspace.editItem(0, 'SPORTS DESK');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content$/);
    });

    describe('multi content widget', function() {
        var widget;

        beforeEach(function() {
            workspace.open();
            workspace.editItem(1);
            authoring.sendTo('Sports Desk');
            workspace.editItem(0, 'SPORTS DESK');
            element(by.id('Aggregate')).click();
            widget = element(by.css('.sd-widget.aggregate'));
        });

        it('can show items grouped by stage', function() {
            // here the math is tricky, because you get here also stages without content that are not visible..
            var stage = element.all(by.repeater('stage in agg.deskStages')).get(4);
            expect(stage.element(by.css('.stage-header')).getText())
                .toBe('SPORTS DESK : NEW\n1');
            expect(stage.all(by.repeater('item in items')).first().element(by.css('.text')).getText())
                .toBe('item1');
        });

        it('can configure stages to be shown', function() {
            widget.element(by.css('.icon-dots-vertical')).click();
            browser.wait(function() {
                return widget.element(by.css('.icon-settings')).isDisplayed();
            });
            widget.element(by.css('.icon-settings')).click();

            // modals are moved around - use last one in dom
            var modal = element.all(by.css('.aggregate-widget-config')).last();
            // pick first desk - politics
            modal.all(by.repeater('desk in agg.desks')).first()
                .element(by.model('agg.active[desk._id]')).click();
            // pick stage one that has some content
            modal.all(by.repeater('stage in agg.deskStages')).get(1)
                .element(by.model('agg.active[stage._id]')).click();
            modal.element(by.buttonText('SAVE')).click();

            expect(element.all(by.repeater('desk in agg.desks')).count()).toBe(1);
            expect(element.all(by.repeater('stage in agg.deskStages')).count()).toBe(1);
        });

        it('can search content', function() {
            widget.element(by.model('query')).sendKeys('item5');
            expect(widget.all(by.repeater('item in items')).count()).toBe(1);
        });
    });
});
