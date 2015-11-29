
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content,
    globalSearch = require('./helpers/search'),
    authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring');

describe('search', function() {

    beforeEach(function() {
        openUrl('/#/search').then(globalSearch.setListView());
    });

    it('can search by search field', function() {
        expect(globalSearch.getItems().count()).toBe(11);
        globalSearch.searchInput.click();
        globalSearch.searchInput.clear();
        globalSearch.searchInput.sendKeys('item3');
        var focused = browser.driver.switchTo().activeElement().getAttribute('id');
        expect(globalSearch.searchInput.getAttribute('id')).toEqual(focused);
        element(by.id('search-button')).click();
        expect(globalSearch.getItems().count()).toBe(1);
    });

    it('can search by search within field', function() {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);

        var searchTextbox = element(by.id('search_within'));
        searchTextbox.clear();
        searchTextbox.sendKeys('item3');
        element(by.id('search_within_button')).click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedKeywords')).count()).toBe(1);
    });

    it('can search by search within field with parenthesis and clear by tag', function() {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);

        var searchTextbox = element(by.id('search_within'));
        searchTextbox.clear();
        searchTextbox.sendKeys('(item3)');
        element(by.id('search_within_button')).click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedKeywords')).count()).toBe(1);
        element(by.css('.icon-close-small')).click();
        expect(globalSearch.getItems().count()).toBe(11);
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

    it('can search by priority field', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        expect(globalSearch.getPriorityElements().count()).toBe(3);
        var priority = globalSearch.getPriorityElementByIndex(0);
        priority.click();
        expect(globalSearch.getItems().count()).toBe(1);
    });

    it('can search by byline field', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        globalSearch.openParameters();
        var bylineTextbox = element(by.id('search-byline'));
        bylineTextbox.clear();
        bylineTextbox.sendKeys('Billy The Fish');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
    });

    it('can search by slugline', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        globalSearch.openParameters();
        var bylineTextbox = element(by.id('search-slugline'));
        bylineTextbox.clear();
        bylineTextbox.sendKeys('one/two');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
    });

    it('can search by slugline with parenthesis and clear by tag', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        globalSearch.openParameters();
        var bylineTextbox = element(by.id('search-slugline'));
        bylineTextbox.clear();
        bylineTextbox.sendKeys('(one/two)');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(element.all(by.repeater('parameter in tags.selectedParameters')).count()).toBe(1);
        element(by.css('.icon-close-small')).click();
        expect(globalSearch.getItems().count()).toBe(11);
    });

    it('can search by original creator', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        globalSearch.openParameters();
        globalSearch.selectCreator('search-creator', 'first name last name');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(10);
    });

    it('can search by genre field', function () {
        globalSearch.openFilterPanel();
        expect(globalSearch.getItems().count()).toBe(11);
        expect(globalSearch.getGenreElements().count()).toBe(1);
        var genre = globalSearch.getGenreElementByIndex(0);
        genre.click();
        expect(globalSearch.getItems().count()).toBe(1);
    });

    it('search by from desk field', function() {
        monitoring.openMonitoring();
        monitoring.switchToDesk('SPORTS DESK').then(authoring.createTextItem());
        authoring.writeTextToHeadline('From-Sports-To-Politics');
        authoring.writeText('This is Body');
        authoring.writeTextToAbstract('This is Abstract');
        authoring.save();
        authoring.sendTo('Politic Desk');
        authoring.confirmSendTo();
        monitoring.switchToDesk('POLITIC DESK');
        expect(monitoring.getTextItem(1, 0)).toBe('From-Sports-To-Politics');

        globalSearch.openGlobalSearch();
        globalSearch.setListView();
        expect(globalSearch.getItems().count()).toBe(12);
        globalSearch.openFilterPanel();
        globalSearch.openParameters();

        globalSearch.selectDesk('from-desk', 'Sports Desk');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(globalSearch.getHeadlineElement(0).getText()).toBe('From-Sports-To-Politics');

        globalSearch.selectDesk('to-desk', 'Politic Desk');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(globalSearch.getHeadlineElement(0).getText()).toBe('From-Sports-To-Politics');

        globalSearch.selectDesk('from-desk', '');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(1);
        expect(globalSearch.getHeadlineElement(0).getText()).toBe('From-Sports-To-Politics');

        globalSearch.selectDesk('to-desk', '');
        globalSearch.goButton.click();
        expect(globalSearch.getItems().count()).toBe(12);
    });

    it('can dynamically update items in related tab when item duplicated', function() {
        expect(globalSearch.getItems().count()).toBe(11);

        globalSearch.actionOnItem('Duplicate', 0);
        globalSearch.itemClick(0);
        monitoring.tabAction('related');
        expect(globalSearch.getRelatedItems().count()).toBe(1);

        globalSearch.actionOnItem('Duplicate', 0);
        globalSearch.itemClick(0);
        monitoring.tabAction('related');
        expect(globalSearch.getRelatedItems().count()).toBe(2);
    });

    it('can disable when no repo is selected and enable if at lease one repo is selected', function () {
        globalSearch.openFilterPanel();
        globalSearch.openParameters();

        globalSearch.ingestRepo.click();
        globalSearch.archiveRepo.click();
        globalSearch.publishedRepo.click();
        globalSearch.archivedRepo.click();

        expect(globalSearch.goButton.isEnabled()).toBe(false);

        globalSearch.ingestRepo.click();
        expect(globalSearch.goButton.isEnabled()).toBe(true);
    });
});
