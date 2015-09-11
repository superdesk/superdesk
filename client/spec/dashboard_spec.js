
'use strict';

var dashboard = require('./helpers/dashboard'),
    workspace = require('./helpers/workspace');

describe('dashboard', function() {

    beforeEach(function() {
        dashboard.openDashboard();
    });

    it('add a widget to a desk', function() {
        expect(dashboard.getWidgets().count()).toBe(0);
        dashboard.showDashboardSettings();
        dashboard.addWidget(0);
        dashboard.doneAction();
        expect(dashboard.getWidgets().count()).toBe(1);
        workspace.selectDesk('Sports Desk');
        expect(dashboard.getWidgets().count()).toBe(0);
        workspace.selectDesk('Politic Desk');
        expect(dashboard.getWidgets().count()).toBe(1);
    });

});
