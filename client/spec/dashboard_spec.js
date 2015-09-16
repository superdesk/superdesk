
'use strict';

var dashboard = require('./helpers/dashboard'),
    workspace = require('./helpers/workspace'),
    monitoring = require('./helpers/monitoring');

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

    it('add multiple monitoring widgets', function() {
        dashboard.showDashboardSettings();
        dashboard.addWidget(4);
        dashboard.addWidget(4);
        dashboard.doneAction();
        expect(dashboard.getWidgets().count()).toBe(2);
        expect(dashboard.getGroups(0).count()).toBe(4);

        expect(dashboard.getTextItem(0, 1, 0)).toBe('item5');
        expect(dashboard.getTextItem(0, 2, 0)).toBe('item6');
        expect(dashboard.getTextItem(1, 1, 0)).toBe('item5');
        expect(dashboard.getTextItem(1, 2, 0)).toBe('item6');

        dashboard.showMonitoringSettings(0);
        monitoring.toggleDesk(0);
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 1);
        monitoring.toggleStage(1, 3);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(dashboard.getTextItem(0, 0, 0)).toBe('item3');
        expect(dashboard.getTextItem(0, 1, 0)).toBe('item4');
        expect(dashboard.getTextItem(1, 1, 0)).toBe('item5');
        expect(dashboard.getTextItem(1, 2, 0)).toBe('item6');
    });

});
