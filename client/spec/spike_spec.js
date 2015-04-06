
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
        element.all(by.repeater('items._items')).count().then(function(count) {
            personalCount = count;
        });

        content.actionOnItem('Spike Item', 0);

        // check that there are less items than before
        browser.wait(function() {
            return element.all(by.repeater('items._items')).count().then(function(count) {
                return count < personalCount;
            });
        }, 3000);
    });
});
