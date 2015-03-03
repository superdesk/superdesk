
'use strict';

var openUrl = require('./helpers/utils').open,
    workspace = require('./helpers/pages').workspace;

describe('Spike', function() {

    beforeEach(openUrl('/#/workspace/content'));

    xit('can spike item', function() {
        workspace.openPersonal();

        var personalCount;
        element.all(by.repeater('items._items')).count().then(function(count) {
             personalCount = count;
        });

        // select & fetch item
        $('body').sendKeys(protractor.Key.DOWN);

        // spike via dropdown menu
        browser.sleep(200);
        element(by.css('.action-menu button.dropdown-toggle')).click();
        browser.sleep(200);
        element(by.css('.action-menu .activity-spike')).click();

        // check that there are more items than before
        browser.wait(function() {
            return element.all(by.repeater('items._items')).count().then(function(count) {
                return count < personalCount;
            });
        }, 3000);
    });
});
