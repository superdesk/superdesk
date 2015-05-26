
'use strict';

var workspace = require('./helpers/workspace');

describe('authoring', function() {
    xit('can open item stage', function() { // obsolete?
        workspace.open();
        workspace.editItem(0, 'SPORTS DESK');
        element(by.css('button.stage')).click();
        expect(browser.getCurrentUrl()).toMatch(/workspace\/content$/);
    });
});
