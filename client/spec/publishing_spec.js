'use strict';

var monitoring = require('./helpers/monitoring'),
    publishQueue = require('./helpers/publish_queue');

describe('publish queue', function() {
    it('publish using HTTP Push delivery type', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        expect(publishQueue.getHeadline(0).getText()).toMatch(/item5/);
        expect(publishQueue.getDestination(0).getText()).toMatch(/HTTP Push/);
    });
    it('can preview content', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        publishQueue.previewAction(0);
        expect(publishQueue.getPreviewTitle()).toBe('item5');
    });
    it('can search item by headline', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        publishQueue.searchAction('item5');
        expect(publishQueue.getItemCount()).toBe(1);
        publishQueue.searchAction('item6');
        browser.sleep(100);
        expect(publishQueue.getItemCount()).toBe(0);
    });
    it('can search item by unique name', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        var _uniqueName = publishQueue.getUniqueName(0).getText();
        publishQueue.searchAction(_uniqueName);
        expect(publishQueue.getItemCount()).toBe(1);
    });
    it('can open item inside the composite item', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        publishQueue.previewAction(0);
        expect(publishQueue.getPreviewTitle()).toBe('item5');
        var _compositeItemHeadline = publishQueue.getCompositeItemHeadline(0);
        publishQueue.openCompositeItem('MAIN');
        browser.sleep(500);
        var _openedItemHeadline = publishQueue.getOpenedItemHeadline();
        browser.sleep(100);
        expect(_openedItemHeadline).toBe(_compositeItemHeadline);
    });
});
