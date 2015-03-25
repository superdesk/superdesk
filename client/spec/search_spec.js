
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Search', function() {

    beforeEach(function(done) {openUrl('/#/workspace/content').then(done);});

    it('can search by search field', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var searchTextbox = element(by.id('search-input'));
        searchTextbox.clear();
        searchTextbox.sendKeys('item3');
        var focused = browser.driver.switchTo().activeElement().getAttribute('id');
        expect(searchTextbox.getAttribute('id')).toEqual(focused);

        element(by.id('search-button')).click();
        content.setListView();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);
    });

    it('can search by search within field', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var filterPanelButton = element(by.css('.fitler-trigger'));
        filterPanelButton.click();

        var searchTextbox = element(by.id('search_within'));
        searchTextbox.clear();
        searchTextbox.sendKeys('item3');
        element(by.id('search_within_button')).click();
        content.setListView();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedKeywords')).count()).toBe(1);
    });

    it('can filter by state', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var filterPanelButton = element(by.css('.fitler-trigger'));
        filterPanelButton.click();

        element.all(by.repeater('(key,value) in aggregations.state'))
        .first().element(by.css('.sd-checkbox')).click();
        content.setListView();

        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        expect(element.all(by.repeater('(type,keys) in tags.selectedFacets')).count()).toBe(1);
    });
});
