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
});
