
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace,
    content = require('./helpers/pages').content;

describe('Spike', function() {

    beforeEach(function(done) {
        openUrl('/#/workspace/content').then(done);
    });

    it('can spike item', function() {
        workspace.switchToDesk('PERSONAL');
        content.setListView();

        var personalCount;
        content.getItems().count().then(function(count) {
            personalCount = count;
        });

        content.actionOnItem('Spike Item', 0);

        // check that there are less items than before
        browser.wait(function() {
            return content.getItems().count().then(function(count) {
                return count < personalCount;
            });
        }, 3000);
    });

    it('can spike and unspike multiple items', function() {
        workspace.switchToDesk('PERSONAL');
        content.setListView();

        var personalCount;
        element.all(by.repeater('items._items')).count().then(function(count) {
            personalCount = count;
        });

        content.selectItem(1);
        content.selectItem(2);
        content.spikeItems();

        // check that there are 2 fewer items than before
        browser.wait(function() {
            return content.getItems().count().then(function(count) {
                return count === (personalCount - 2);
            });
        }, 3000);

        content.selectSpikedList();

        // check that there are 2 items
        browser.wait(function() {
            return content.getItems().count().then(function(count) {
                return count === 2;
            });
        }, 3000);

        content.selectItem(0);
        content.selectItem(1);
        content.unspikeItems();

        // check that there are 0 items
        browser.wait(function() {
            return content.getItems().count().then(function(count) {
                return count === 0;
            });
        }, 3000);

        content.selectSpikedList();

        // check that there are personalCount items
        browser.wait(function() {
            return content.getItems().count().then(function(count) {
                return count === personalCount;
            });
        }, 3000);
    });
});
