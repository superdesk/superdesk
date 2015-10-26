
'use strict';

var monitoring = require('./helpers/monitoring'),
    search = require('./helpers/search'),
    authoring = require('./helpers/authoring'),
    ctrlKey = require('./helpers/utils').ctrlKey;

describe('authoring', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
    });

    it('authoring operations', function() {
        //undo and redo operations by using CTRL+Z and CTRL+y
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        expect(authoring.getBodyText()).toBe('item5 text');
        authoring.writeText('Two');
        expect(authoring.getBodyText()).toBe('Twoitem5 text');
        authoring.writeText('Words');
        expect(authoring.getBodyText()).toBe('TwoWordsitem5 text');
        ctrlKey('z');
        expect(authoring.getBodyText()).toBe('Twoitem5 text');
        ctrlKey('y');
        expect(authoring.getBodyText()).toBe('TwoWordsitem5 text');
        authoring.save();
        authoring.close();

        //allows to create a new empty package
        monitoring.createItemAction('create_package');
        expect(element(by.className('packaging-screen')).isDisplayed()).toBe(true);
        authoring.close();

        //can edit packages in which the item was linked
        expect(monitoring.getTextItem(1, 1)).toBe('item9');
        monitoring.actionOnItem('Edit', 1, 1);
        authoring.showPackages();
        expect(authoring.getPackages().count()).toBe(1);
        expect(authoring.getPackage(0).getText()).toMatch('PACKAGE2');
        authoring.getPackage(0).click();
        authoring.showInfo();
        expect(authoring.getGUID().getText()).toMatch('package2');
        authoring.close();

        //can change normal theme
        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.changeNormalTheme('dark-theme');
        expect(monitoring.hasClass(element(by.className('main-article')), 'dark-theme')).toBe(true);
        authoring.close();

        //can change proofread theme
        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.changeProofreadTheme('dark-theme-mono');
        expect(monitoring.hasClass(element(by.className('main-article')), 'dark-theme-mono')).toBe(true);
        authoring.close();

        //publish & kill item
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.publish();
        monitoring.showSearch();
        search.setListView();
        search.showCustomSearch();
        search.toggleByType('text');
        expect(search.getTextItem(0)).toBe('item5');
        search.actionOnItem('Kill item', 0);
        authoring.sendToButton.click();
        expect(authoring.kill_button.isDisplayed()).toBe(true);

        //publish & correct item
        monitoring.openMonitoring();
        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.publish();
        monitoring.showSearch();
        search.setListView();
        search.showCustomSearch();
        search.toggleByType('text');
        expect(search.getTextItem(0)).toBe('item6');
        search.actionOnItem('Correct item', 0);
        authoring.sendToButton.click();
        expect(authoring.correct_button.isDisplayed()).toBe(true);
        authoring.close();
        expect(search.getTextItem(0)).toBe('item6');
        search.actionOnItem('Open', 0);
        expect(authoring.edit_correct_button.isDisplayed()).toBe(true);
        expect(authoring.edit_kill_button.isDisplayed()).toBe(true);
        authoring.close();
        search.toggleByType('text');
        search.toggleByType('composite');
        expect(search.getTextItem(0)).toBe('item6');
        search.actionOnItem('Open', 0);
        expect(authoring.edit_correct_button.isDisplayed()).toBe(false);
        expect(authoring.edit_kill_button.isDisplayed()).toBe(false);
    });

    it('authoring history', function() {
        //view item history create-fetch operation
        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(1);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Fetched as \d+ to Politic Desk\/two by.*/);
        authoring.close();

        //view item history move operation
        expect(monitoring.getTextItem(1, 3)).toBe('item8');
        monitoring.actionOnItem('Edit', 1, 3);
        authoring.writeText('Two');
        authoring.save();
        expect(authoring.sendToButton.isDisplayed()).toBe(true);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        authoring.sendTo('Politic Desk', 'two');
        authoring.confirmSendTo();
        expect(monitoring.getTextItem(2, 0)).toBe('item8');
        monitoring.actionOnItem('Edit', 2, 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Moved to Politic Desk\/two by .*/);
        authoring.close();

        //view item history create-update operations
        authoring.createTextItem();
        authoring.writeTextToHeadline('new item');
        authoring.writeText('some text');
        authoring.save();
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(0).getText()).toMatch(/Story \d+ Created by.*/);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Updated by.*/);
        authoring.save();
        authoring.close();

        //view item history publish operation
        expect(monitoring.getTextItem(2, 3)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 3);
        authoring.publish();
        monitoring.showSearch();
        search.setListView();
        search.showCustomSearch();
        search.toggleByType('text');
        expect(search.getTextItem(0)).toBe('item6');
        search.actionOnItem('Open', 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Published by.*/);
        authoring.close();
        monitoring.showMonitoring();

        //view item history spike-unspike operations
        expect(monitoring.getTextItem(1, 2)).toBe('item7');
        monitoring.actionOnItem('Spike', 1, 2);
        monitoring.showSpiked();
        expect(monitoring.getSpikedTextItem(0)).toBe('item7');
        monitoring.unspikeItem(0);
        monitoring.showMonitoring();
        expect(monitoring.getTextItem(0, 0)).toBe('item7');
        monitoring.actionOnItem('Edit', 0, 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(3);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Spiked from Politic Desk\/one by .*/);
        expect(authoring.getHistoryItem(2).getText()).toMatch(/Unspiked to Politic Desk\/one by .*/);
        authoring.close();

        //view item history duplicate operation
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Duplicate', 1, 0);
        monitoring.showSpiked();
        monitoring.showMonitoring();
        expect(monitoring.getTextItem(0, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 0, 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Copied to \d+ \(Politic Desk\/New\) by .*/);
        authoring.close();
    });

    it('keyboard shortcuts', function() {
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.writeText('z');
        element(by.cssContainingText('span', 'Headline')).click();
        ctrlKey('s');
        browser.wait(function() {
            return element(by.buttonText('SAVE')).getAttribute('disabled');
        }, 500);
        authoring.close();
        monitoring.actionOnItem('Edit', 1, 0);
        browser.sleep(300);

        expect(authoring.getBodyText()).toBe('zitem5 text');

        element(by.cssContainingText('span', 'Headline')).click();
        ctrlKey('q');
        browser.sleep(300);

        expect(element(by.className('authoring-embedded')).isDisplayed()).toBe(false);
    });
});
