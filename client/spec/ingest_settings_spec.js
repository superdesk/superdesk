'use strict';
var openUrl = require('./helpers/utils').open,
    ingestSettings = require('./helpers/pages').ingestSettings,
    utils = require('./helpers/utils');

describe('Ingest Settings: routing scheme', function() {

    beforeEach(function(done) {
        openUrl('/#/settings/ingest').then(done);
    });

    it('unselecting options in dropdown lists on the Actions pane', function () {
        var deskList,   // dropdown list for choosing a desk
            macroList,  // dropdown list for choosing a macro
            stageList,  // dropdown list for choosing a desk stage
            ruleSettings;

        // open the routing scheme edit modal under the  Routing tab, add a new
        // routing rule and open its Action settings pane
        ingestSettings.tabs.routingTab.click();
        ingestSettings.newSchemeBtn.click();

        ingestSettings.writeTextToSchemeName('Test Scheme');

        ingestSettings.newRoutingRuleBtn.click();
        ruleSettings = ingestSettings.routingRuleSettings;
        ruleSettings.tabAction.click();

        // Select values in the three dropdown lists under the FETCH section,
        // then try to deselect them, i.e. select an empty option. If the
        // latter exists, the value of the selected options in all lists should
        // be empty.
        ruleSettings.showFetchBtn.click();

        deskList = ruleSettings.fetchDeskList;
        utils.getListOption(deskList, 2).click();

        stageList = ruleSettings.fetchStageList;
        utils.getListOption(stageList, 2).click();

        macroList = ruleSettings.fetchMacroList;
        utils.getListOption(macroList, 2).click();

        // now select first options and then check that they are all blank
        utils.getListOption(deskList, 1).click();
        utils.getListOption(stageList, 1).click();
        utils.getListOption(macroList, 1).click();

        expect(deskList.$('option:checked').getAttribute('value')).toEqual('');
        expect(stageList.$('option:checked').getAttribute('value')).toEqual('');
        expect(macroList.$('option:checked').getAttribute('value')).toEqual('');

        // We now perform the same check for the dropdown menus under the
        // PUBLISH section
        ruleSettings.showPublishBtn.click();

        deskList = ruleSettings.publishDeskList;
        utils.getListOption(deskList, 2).click();

        stageList = ruleSettings.publishStageList;
        utils.getListOption(stageList, 2).click();

        macroList = ruleSettings.publishMacroList;
        utils.getListOption(macroList, 2).click();

        utils.getListOption(deskList, 1).click();
        utils.getListOption(stageList, 1).click();
        utils.getListOption(macroList, 1).click();

        expect(deskList.$('option:checked').getAttribute('value')).toEqual('');
        expect(stageList.$('option:checked').getAttribute('value')).toEqual('');
        expect(macroList.$('option:checked').getAttribute('value')).toEqual('');
    });

    it('contains the Schedule tab for editing routing schedules', function () {
        var ruleSettings,
            tzOption;

        // Open the routing scheme edit modal under the Routing tab and set
        // routing scheme name.
        // Then add a new routing rule and set its name, and open the Schedule
        // settings pane
        ingestSettings.tabs.routingTab.click();
        ingestSettings.newSchemeBtn.click();
        ingestSettings.schemeNameInput.sendKeys('My Routing Scheme');

        ruleSettings = ingestSettings.routingRuleSettings;
        ingestSettings.newRoutingRuleBtn.click();
        ruleSettings.ruleNameInput.sendKeys('Routing Rule 1');

        ruleSettings.tabSchedule.click();

        // one the Schedule tab now, set a few scheduling options...
        // de-select Saturday and Sunday
        ruleSettings.daysButtons.sat.click();
        ruleSettings.daysButtons.sun.click();

        // pick the time zone
        ruleSettings.timezoneInput.sendKeys('Asia/Singapore');
        tzOption = ruleSettings.timezoneList.get(0);
        browser.driver.wait(protractor.until.elementIsVisible(tzOption), 3000);
        tzOption.click();

        // save the routing scheme and check that it was successfull
        ingestSettings.saveBtn.click();

        utils.assertToastMsg('success', 'Routing scheme saved');
    });

    it('cannot add blank rule', function() {
        ingestSettings.tabs.routingTab.click();
        ingestSettings.newSchemeBtn.click();
        ingestSettings.writeTextToSchemeName('Test Scheme');
        ingestSettings.newRoutingRuleBtn.click();

        expect(ingestSettings.getTextfromRuleName()).toBe('');
        expect(ingestSettings.newRoutingRuleBtn.getAttribute('disabled')).toBeTruthy();

        ingestSettings.writeTextToRuleName('Test Rule');
        expect(ingestSettings.getTextfromRuleName()).toBe('Test Rule');
        expect(ingestSettings.newRoutingRuleBtn.getAttribute('disabled')).toBeFalsy();

    });
});
