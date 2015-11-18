'use strict';
var openUrl = require('./helpers/utils').open,
    ingestDashboard = require('./helpers/pages').ingestDashboard;

describe('Ingest Provider Dashboard Maintenance', function() {

    beforeEach(function(done) {
        openUrl('/#/ingest_dashboard').then(done);
    });

    function addProvider() {
        ingestDashboard.openDropDown();
        var providerButton = ingestDashboard.getProviderButton(ingestDashboard.getProvider(0));
        expect(providerButton.getAttribute('class')).not.toContain('checked');
        providerButton.click();
        expect(providerButton.getAttribute('class')).toContain('checked');

        // for the add board to appear.
        browser.wait(function() {
            return ingestDashboard.getDashboard(0).isDisplayed();
        }, 1000);

        ingestDashboard.getDashboard(0).click();
    }

    it('add ingest provider to dashboard', function() {
        addProvider();
    });

    it('remove ingest provider to dashboard', function() {
        addProvider();
        ingestDashboard.openDropDown();
        var providerButton = ingestDashboard.getProviderButton(ingestDashboard.getProvider(0));
        expect(providerButton.getAttribute('class')).toContain('checked');
        providerButton.click();
        expect(providerButton.getAttribute('class')).not.toContain('checked');
        expect(ingestDashboard.getDashboardList().count()).toEqual(0);
    });

    it('Change settings for Ingest Provider', function() {
        addProvider();
        expect(ingestDashboard.getDashboardList().count()).toEqual(1);
        var dashboard = ingestDashboard.getDashboard(0);
        var settings = ingestDashboard.getDashboardSettings(dashboard);
        settings.click();

        //status
        expect(ingestDashboard.getDashboardStatus(dashboard).isDisplayed()).toBe(true);
        ingestDashboard.getDashboardSettingsStatusButton(settings).click();
        expect(ingestDashboard.getDashboardStatus(dashboard).isDisplayed()).toBe(false);

        //ingest count
        expect(ingestDashboard.getDashboardIngestCount(dashboard).isDisplayed()).toBe(true);
        ingestDashboard.getDashboardSettingsIngestCountButton(settings).click();
        expect(ingestDashboard.getDashboardIngestCount(dashboard).isDisplayed()).toBe(false);
    });

    it('Go to Ingest Providers', function() {
        ingestDashboard.openDropDown();
        ingestDashboard.dropDown.element(by.css('.icon-pencil')).click();

        browser.wait(function() {
            return element(by.id('ingest-settings')).isDisplayed();
        }, 1000).then(function() {
            expect(element(by.id('ingest-settings')).isDisplayed()).toBe(true);
        });
    });

    it('Go to Ingest Providers and open dialog', function() {
        addProvider();
        var dashboard = ingestDashboard.getDashboard(0);
        var settings = ingestDashboard.getDashboardSettings(dashboard);
        settings.click();
        settings.element(by.css('.icon-pencil')).click();

        browser.wait(function() {
            return element(by.id('ingest-settings')).isDisplayed();
        }, 1000).then(function() {
            expect(element(by.id('ingest-settings')).isDisplayed()).toBe(true);
            expect(element(by.css('.modal-dialog')).element(by.id('provider-name')).isDisplayed()).toBe(true);
        });
    });
});
