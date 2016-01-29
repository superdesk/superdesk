
'use strict';

var dashboard = require('./helpers/dashboard'),
    workspace = require('./helpers/workspace'),
    authoring = require('./helpers/authoring'),
    monitoring = require('./helpers/monitoring');

describe('dashboard', function() {

    beforeEach(function() {
        dashboard.openDashboard();
    });

    it('add a widget to a desk', function() {
        expect(dashboard.getWidgets().count()).toBe(0);
        dashboard.showDashboardSettings();
        dashboard.addWidget(1);
        dashboard.doneAction();
        expect(dashboard.getWidgets().count()).toBe(1);
        workspace.selectDesk('Sports Desk');
        expect(dashboard.getWidgets().count()).toBe(0);
        workspace.selectDesk('Politic Desk');
        expect(dashboard.getWidgets().count()).toBe(1);
    });

    it('add multiple monitoring widgets', function() {
        dashboard.showDashboardSettings();
        dashboard.addWidget(1);  // the monitoring widget
        dashboard.addWidget(1);  // the monitoring widget
        dashboard.doneAction();
        expect(dashboard.getWidgets().count()).toBe(2);
        expect(dashboard.getGroups(0).count()).toBe(6);

        expect(dashboard.getTextItem(0, 2, 0)).toBe('item5');
        expect(dashboard.getTextItem(0, 3, 2)).toBe('item6');
        expect(dashboard.getTextItem(1, 2, 0)).toBe('item5');
        expect(dashboard.getTextItem(1, 3, 2)).toBe('item6');

        dashboard.showMonitoringSettings(0);
        monitoring.toggleDesk(0);
        monitoring.toggleDesk(1);
        monitoring.toggleStage(1, 2);
        monitoring.toggleStage(1, 4);
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();
        expect(dashboard.getTextItem(0, 0, 0)).toBe('item3');
        expect(dashboard.getTextItem(0, 1, 0)).toBe('item4');
        expect(dashboard.getTextItem(1, 2, 0)).toBe('item5');
        expect(dashboard.getTextItem(1, 3, 2)).toBe('item6');
    });

    it('configure a label for the view', function() {
        dashboard.showDashboardSettings();
        dashboard.addWidget(1);  // the monitoring widget
        dashboard.doneAction();

        dashboard.showMonitoringSettings(0);
        monitoring.setLabel('test');
        monitoring.nextStages();
        monitoring.nextSearches();
        monitoring.nextReorder();
        monitoring.saveSettings();

        expect(dashboard.getWidgetLabel(0)).toBe('test');
    });

    it('search in monitoring widget', function() {
        dashboard.showDashboardSettings();
        dashboard.addWidget(1);  // the monitoring widget
        dashboard.doneAction();
        expect(dashboard.getWidgets().count()).toBe(1);
        expect(dashboard.getGroupItems(0, 2).count()).toBe(4);
        dashboard.doSearch(0, 'item7');
        expect(dashboard.getGroupItems(0, 2).count()).toBe(1);
        expect(dashboard.getTextItem(0, 2, 0)).toBe('item7');
    });

    it('can display desk output in monitoring widget when an item gets published', function() {
        monitoring.openMonitoring();
        monitoring.turnOffWorkingStage(0);

        expect(monitoring.getTextItem(2, 2)).toBe('item6');
        monitoring.actionOnItem('Edit', 2, 2);
        authoring.publish();
        browser.sleep(300);

        dashboard.openDashboard();
        dashboard.showDashboardSettings();
        dashboard.addWidget(1);  // the monitoring widget
        dashboard.doneAction();

        expect(dashboard.getTextItem(0, 5, 1)).toBe('item6');
    });
});
