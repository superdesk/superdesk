'use strict';
var openUrl = require('./helpers/utils').open,
    post = require('./helpers/utils').post,
    ingestProviderDashboard = require('./helpers/pages').ingestProviderDashboard;


describe('Ingest Provider Dashboard', function() {

    beforeEach(function(done) {
        openUrl('/#/ingest_dashboard').then(done);
    });

    it('add ingest provider to dashboard', function() {
        var dropDown;

        ingestProviderDashboard.openDropDown().then(function(elem) {
            var items = ingestProviderDashboard.dropDown.all(by.repeater('item in items'));
            expect(items.count()).toEqual(2);
            // var first = items.first();

            // first.then(function (elem) {
            //     //console.log(elem);
            //     expect(elem.element(by.css('.pull-right'))).toBe(false);
            //     console.log('after');
            // });
            //expect(first.by.model('item.dashboard_enabled'))).toBe(true);

        });

        // openUrl('/#/ingest_dashboard').then(function (result) {
        //     console.log('openurl');
        // }).then(function() {
        //     return element(by.id('ingest-dashboard-dropdown')).click();
        // }).then (function() {
        //     var dropDown = element(by.css('.ingest-dashboard-dropdown'));
        //     expect(dropDown.all(by.repeater('item in items')).count()).toEqual(2);
        // });
        
    });
});