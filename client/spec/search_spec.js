
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Search', function() {

    beforeEach(function(done) {
        openUrl('/#/workspace/content').then(done);
    });

    it('can search by search field', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var searchTextbox = element(by.id('search-input'));
        searchTextbox.clear();
        searchTextbox.sendKeys('item3');
        var focused = browser.driver.switchTo().activeElement().getAttribute('id');
        expect(searchTextbox.getAttribute('id')).toEqual(focused);

        element(by.id('search-button')).click();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);
    });

    it('can search by search within field', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var filterPanelButton = element(by.css('.filter-trigger'));
        filterPanelButton.click();

        var searchTextbox = element(by.id('search_within'));
        searchTextbox.clear();
        searchTextbox.sendKeys('item3');
        element(by.id('search_within_button')).click();
        expect(element.all(by.repeater('items._items')).count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedKeywords')).count()).toBe(1);
    });

    xit('can search by subject codes field', function () {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var filterPanelButton = element(by.css('.filter-trigger'));
        var subject = element.all(by.css('.dropdown-nested')).first();
        var subjectToggle = subject.element(by.css('.dropdown-toggle'));

        filterPanelButton.click();
        element.all(by.css('[ng-click="toggleModule()"]')).first().click();
        subjectToggle.click();
        subject.all(by.css('.nested-toggle')).first().click();
        subject.all(by.repeater('term in activeTree')).first().click();

        expect(element.all(by.repeater('t in item[field]')).count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedParameters')).count()).toBe(1);
        expect(element.all(by.repeater('item in items._items')).count()).toBe(0);
    });

    it('can filter by state', function() {
        workspace.switchToDesk('SPORTS DESK').then(content.setListView);
        expect(element.all(by.repeater('items._items')).count()).toBe(2);

        var filterPanelButton = element(by.css('.filter-trigger'));
        filterPanelButton.click();

        element.all(by.repeater('(key,value) in aggregations.state'))
        .first().element(by.css('.sd-checkbox')).click();

        expect(element.all(by.repeater('items._items')).count()).toBe(2);
        expect(element.all(by.repeater('(type,keys) in tags.selectedFacets')).count()).toBe(1);
    });
});
