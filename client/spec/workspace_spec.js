
'use strict';

var dashboard = require('./helpers/dashboard'),
    altKey = require('./helpers/utils').altKey;

describe('workspace', function () {
    beforeEach(function () {
        dashboard.openDashboard();
    });

    it('can switch views by keyboard', function() {
        // Can switch to monitoring view by pressing alt + m
        altKey('m');
        expect(browser.getLocationAbsUrl()).toMatch('/workspace/monitoring');

        // Can switch to tasks view by pressing alt + t
        altKey('t');
        expect(browser.getLocationAbsUrl()).toMatch('/workspace/tasks');

        // Can switch to spiked view by pressing alt + x
        altKey('x');
        expect(browser.getLocationAbsUrl()).toMatch('/workspace/spike-monitoring');

        // Can switch to personal view by pressing alt + p
        altKey('p');
        expect(browser.getLocationAbsUrl()).toMatch('/workspace/personal');

        // Can switch to search view by pressing alt + s
        altKey('f');
        expect(browser.getLocationAbsUrl()).toMatch('/search');

        // Can get back to dashboard by pressing alt + h
        altKey('h');
        expect(browser.getLocationAbsUrl()).toMatch('/workspace');
    });
});
