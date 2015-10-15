
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/content'),
    authoring = require('./helpers/authoring');

describe('Content', function() {

    var body = element(by.tagName('body'));

    function selectedHeadline() {
        var headline = element(by.className('preview-headline'));

        browser.wait(function() {
            return headline.isDisplayed();
        }, 200); // animated sidebar

        return headline.getText();
    }

    beforeEach(function() {
        openUrl('/#/workspace');
        workspace.switchToDesk('PERSONAL');
        expect(element.all(by.repeater('items._items')).count()).toBe(3);
    });

    // wait a bit after sending keys to body
    function pressKey(key) {
        body.sendKeys(key);
        browser.sleep(50);
    }

    function setEmbargo() {
        var embargoTS = new Date();
        embargoTS.setDate(embargoTS.getDate() + 2);
        var embargoDate = embargoTS.getDate() + '/' + (embargoTS.getMonth() + 1) + '/' +
            embargoTS.getFullYear();
        var embargoTime = embargoTS.toTimeString().slice(0, 8);

        element(by.model('item.embargo_date')).element(by.tagName('input')).sendKeys(embargoDate);
        element(by.model('item.embargo_time')).element(by.tagName('input')).sendKeys(embargoTime);
    }

    it('can navigate with keyboard', function() {
        pressKey(protractor.Key.UP);
        expect(selectedHeadline()).toBe('package1');

        pressKey(protractor.Key.DOWN);
        expect(selectedHeadline()).toBe('item1');

        pressKey(protractor.Key.RIGHT);
        expect(selectedHeadline()).toBe('item2');

        pressKey(protractor.Key.LEFT);
        expect(selectedHeadline()).toBe('item1');

        pressKey(protractor.Key.UP);
        expect(selectedHeadline()).toBe('package1');
    });

    it('can open search with s', function() {
        pressKey('s');
        expect(element(by.id('search-input')).isDisplayed()).toBe(true);
    });

    it('can toggle view with v', function() {
        var gridBtn = element.all(by.css('.view-select button')).first();

        // reset to grid view first
        gridBtn.isDisplayed().then(function(isList) {
            if (isList) {
                gridBtn.click();
            }
        });

        expect(element.all(by.css('.state-border')).count()).toBe(0);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(3);
        body.sendKeys('v');
        expect(element.all(by.css('.state-border')).count()).toBe(0);
    });

    function toggle(selectbox) {
        browser.actions().mouseMove(selectbox).perform();
        selectbox.element(by.css('.sd-checkbox')).click();
    }

    it('can select multiple items', function() {
        content.setListView();
        var count = element(by.id('multi-select-count')),
            boxes = element.all(by.css('.list-field.type-icon'));

        toggle(boxes.first());
        expect(count.getText()).toBe('1 Item selected');

        toggle(boxes.last());
        expect(count.getText()).toBe('2 Items selected');

        element(by.css('.big-icon-multiedit')).click();
        expect(browser.getCurrentUrl()).toMatch(/multiedit$/);
        expect(element.all(by.repeater('board in boards')).count()).toBe(2);
    });

    it('can create text article in a desk', function() {
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();

        element(by.className('sd-create-btn')).click();
        element(by.id('create_text_article')).click();

        authoring.writeText('Words');
        authoring.save();
        authoring.close();

        expect(content.count()).toBe(3);
    });

    it('can create empty package in a desk', function() {
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();

        element(by.className('sd-create-btn')).click();
        element(by.id('create_package')).click();

        element.all(by.model('item.headline')).first().sendKeys('Empty Package');
        authoring.save();
        authoring.close();

        expect(content.count()).toBe(3);
    });

    it('can close unsaved empty package in a desk', function() {
        workspace.switchToDesk('SPORTS DESK');
        content.setListView();

        element(by.className('sd-create-btn')).click();
        element(by.id('create_package')).click();

        element.all(by.model('item.headline')).first().sendKeys('Empty Package');
        authoring.close();

        element.all(by.className('btn-warning')).first().click();
        expect(content.count()).toBe(2);
    });

    it('can open item using hotkey ctrl+0', function() {
        content.setListView();

        browser.actions().sendKeys(protractor.Key.chord(protractor.Key.CONTROL, '0')).perform();
        browser.sleep(500);

        var storyNameEl = element(by.model('meta.unique_name'));
        expect(storyNameEl.isDisplayed()).toBe(true);

        storyNameEl.clear();
        storyNameEl.sendKeys('item1');

        element(by.id('searchItemByNameBtn')).click();
        browser.sleep(500);

        expect(content.getItemType('text').isDisplayed()).toBe(true);
        expect(content.getWidgets().count()).toBe(7);

        element(by.id('closeAuthoringBtn')).click();
    });

    it('can open package using hotkey ctrl+0', function() {
        content.setListView();

        browser.actions().sendKeys(protractor.Key.chord(protractor.Key.CONTROL, '0')).perform();
        browser.sleep(500);

        var storyNameEl = element(by.model('meta.unique_name'));
        expect(storyNameEl.isDisplayed()).toBe(true);

        storyNameEl.clear();
        storyNameEl.sendKeys('package1');

        element(by.id('searchItemByNameBtn')).click();
        browser.sleep(500);

        expect(content.getItemType('composite').isDisplayed()).toBe(true);
        expect(content.getWidgets().count()).toBe(6);

        element(by.id('closeAuthoringBtn')).click();
    });

    it('can display embargo in metadata when set', function() {
        workspace.editItem('item3', 'SPORTS');
        authoring.sendToButton.click();

        setEmbargo();

        element(by.css('[ng-click="saveTopbar(item)"]')).click();
        element(by.id('closeAuthoringBtn')).click();

        content.previewItem('item3');
        element(by.css('[ng-click="tab = \'metadata\'"]')).click();
        expect(element(by.model('item.embargo')).isDisplayed()).toBe(true);
        content.closePreview();
    });

    it('cannot display embargo items in search widget of the package', function() {
        workspace.editItem('item3', 'SPORTS');
        authoring.sendToButton.click();

        setEmbargo();

        element(by.css('[ng-click="saveTopbar(item)"]')).click();
        element(by.id('closeAuthoringBtn')).click();

        element(by.className('sd-create-btn')).click();
        element(by.id('create_package')).click();

        element(by.id('Search')).click();
        element(by.className('search-box')).element(by.model('query')).sendKeys('item3');
        expect(element.all(by.repeater('pitem in contentItems')).count()).toBe(0);
    });

    it('can enable/disable send and continue based on emabrgo', function() {
        workspace.editItem('item3', 'SPORTS');
        authoring.sendToButton.click();

        // Initial State
        expect(authoring.sendAndContinueBtn.isEnabled()).toBe(false);
        expect(authoring.sendBtn.isEnabled()).toBe(false);

        var sidebar = element.all(by.css('.slide-pane')).last(),
            dropdown = sidebar.element(by.css('.dropdown--dark .dropdown-toggle'));

        dropdown.waitReady();

        // State after selecting different Stage in the same desk
        sidebar.element(by.buttonText('two')).click();
        expect(authoring.sendAndContinueBtn.isEnabled()).toBe(true);
        expect(authoring.sendBtn.isEnabled()).toBe(true);

        // State after setting Embargo
        setEmbargo();
        expect(authoring.sendAndContinueBtn.isEnabled()).toBe(false);
        expect(authoring.sendBtn.isEnabled()).toBe(true);

        //State after changing Desk
        dropdown.click();
        sidebar.element(by.buttonText('Politic Desk')).click();
        expect(authoring.sendAndContinueBtn.isEnabled()).toBe(false);
        expect(authoring.sendBtn.isEnabled()).toBe(true);
    });

});
