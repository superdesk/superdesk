'use strict';

var monitoring = require('./helpers/monitoring'),
    authoring = require('./helpers/authoring'),
    ctrlKey = require('./helpers/utils').ctrlKey,
    ctrlShiftKey = require('./helpers/utils').ctrlShiftKey,
    assertToastMsg = require('./helpers/utils').assertToastMsg;

describe('authoring', function() {

    beforeEach(function() {
        monitoring.openMonitoring();
        monitoring.turnOffWorkingStage(0);
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
        authoring.getPackage(0).element(by.tagName('a')).click();
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
        monitoring.filterAction('text');
        monitoring.actionOnItem('Kill item', 4, 0);
        authoring.sendToButton.click();
        expect(authoring.kill_button.isDisplayed()).toBe(true);

        //publish & correct item
        monitoring.openMonitoring();
        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.publish();
        monitoring.filterAction('text');
        monitoring.actionOnItem('Correct item', 4, 0);
        authoring.sendToButton.click();
        expect(authoring.correct_button.isDisplayed()).toBe(true);
        authoring.close();
        expect(monitoring.getTextItem(4, 0)).toBe('item6');
        monitoring.actionOnItem('Open', 4, 0);
        expect(authoring.edit_correct_button.isDisplayed()).toBe(true);
        expect(authoring.edit_kill_button.isDisplayed()).toBe(true);
        authoring.close();
        monitoring.filterAction('text');
        monitoring.filterAction('composite');
        expect(monitoring.getTextItem(4, 0)).toBe('item6');
        monitoring.actionOnItem('Open', 4, 0);
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
        authoring.addPublicServiceAnnouncement('Children');
        expect(authoring.getBodyFooter()).toMatch(/Kids Helpline*/);
        authoring.publish();
        monitoring.filterAction('composite');
        monitoring.actionOnItem('Open', 4, 0);
        authoring.showHistory();
        expect(authoring.getHistoryItems().count()).toBe(2);
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Published by.*/);
        var transmissionDetails = authoring.showTransmissionDetails(1);
        expect(transmissionDetails.count()).toBe(1);
        transmissionDetails.get(0).click();
        expect(element(by.className('modal-body')).getText()).toMatch(/Kids Helpline*/);
        element(by.css('[ng-click="hideFormattedItem()"]')).click();
        monitoring.filterAction('composite');
        authoring.close();

        //view item history spike-unspike operations
        browser.sleep(5000);
        monitoring.showMonitoring();
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
        expect(authoring.getHistoryItem(1).getText()).toMatch(/Copied to \d+ \(Politic Desk\/Incoming Stage\) by .*/);
        authoring.close();
    });

    it('keyboard shortcuts', function() {
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.writeText('z');
        element(by.cssContainingText('span', 'Headline')).click();
        ctrlShiftKey('s');
        browser.wait(function() {
            return element(by.buttonText('SAVE')).getAttribute('disabled');
        }, 500);
        authoring.close();
        monitoring.actionOnItem('Edit', 1, 0);
        browser.sleep(300);

        expect(authoring.getBodyText()).toBe('zitem5 text');

        element(by.cssContainingText('span', 'Headline')).click();
        ctrlShiftKey('e');
        browser.sleep(300);

        expect(element(by.className('authoring-embedded')).isDisplayed()).toBe(false);
    });

    it('can display monitoring after publishing an item using full view of authoring', function () {
        monitoring.actionOnItem('Edit', 2, 2);
        monitoring.showHideList();

        authoring.publish();
        expect(monitoring.getGroups().count()).toBe(5);
    });

    it('broadcast operation', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.publish();
        monitoring.filterAction('text');
        monitoring.actionOnItem('Create Broadcast', 4, 0);
        expect(element(by.className('content-item-preview')).isDisplayed()).toBe(true);
        expect(monitoring.getPreviewTitle()).toBe('item5');
        monitoring.closePreview();

        authoring.linkToMasterButton.click();
        expect(monitoring.getPreviewTitle()).toBe('item5');
        authoring.close();
    });

    it('toggle auto spellcheck and hold changes', function() {
        monitoring.actionOnItem('Edit', 1, 1);
        expect(element(by.model('spellcheckMenu.isAuto')).getAttribute('checked')).toBeTruthy();
        authoring.toggleAutoSpellCheck();
        expect(element(by.model('spellcheckMenu.isAuto')).getAttribute('checked')).toBeFalsy();
        authoring.close();
        monitoring.actionOnItem('Edit', 1, 2);
        expect(element(by.model('spellcheckMenu.isAuto')).getAttribute('checked')).toBeFalsy();
    });

    it('related item widget', function() {
        monitoring.actionOnItem('Edit', 1, 1);
        authoring.openRelatedItem();
        expect(authoring.getRelatedItems().count()).toBe(1);
        authoring.searchRelatedItems('item');
        expect(authoring.getRelatedItems().count()).toBe(7);
    });

    it('related item widget can open published item', function() {
        expect(monitoring.getGroups().count()).toBe(5);
        expect(monitoring.getTextItem(1, 1)).toBe('item9');
        expect(monitoring.getTextItemBySlugline(1, 1)).toBe('ITEM9 SLUGLINE');
        monitoring.actionOnItem('Edit', 1, 1);
        authoring.publish(); // item9 published
        browser.sleep(200);

        monitoring.actionOnItem('Duplicate', 4, 1); // duplicate item9 text published item
        expect(monitoring.getGroupItems(0).count()).toBe(1);
        monitoring.actionOnItem('Edit', 0, 0);

        authoring.openRelatedItem(); // opens related item widget
        expect(authoring.getRelatedItemBySlugline(0).getText()).toBe('item9 slugline');
        authoring.getRelatedItemBySlugline(0).click();

        authoring.actionOpenRelatedItem(); // Open item
        expect(authoring.getHeaderSluglineText()).toBe('item9 slugline');
    });

    it('Kill Template apply', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.publish();
        monitoring.filterAction('text');
        monitoring.actionOnItem('Kill item', 4, 0);
        expect(authoring.getBodyText()).toBe('This is kill template. Slugged item5 slugline one/two.');
        expect(authoring.getHeadlineText()).toBe('KILL NOTICE');
        expect(authoring.getHeadlineText()).toBe('KILL NOTICE');
        authoring.sendToButton.click();
        expect(authoring.kill_button.isDisplayed()).toBe(true);
    });

    it('Emptied body text fails to validate', function() {
        expect(monitoring.getTextItem(1, 0)).toBe('item5');
        monitoring.actionOnItem('Edit', 1, 0);
        authoring.writeText('');
        ctrlShiftKey(protractor.Key.END);
        ctrlKey('x');
        authoring.save();
        authoring.publish();
        assertToastMsg('error', 'BODY_HTML empty values not allowed');
    });
});
