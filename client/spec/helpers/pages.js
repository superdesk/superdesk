'use strict';

exports.login = LoginModal;
exports.workspace = require('./workspace');
exports.content = require('./content');
exports.authoring = require('./authoring');
exports.ingestProvider = new IngestProvider();
exports.ingestDashboard = new IngestDashboard();

require('./waitReady');

function LoginModal() {
    this.username = element(by.model('username'));
    this.password = element(by.model('password'));
    this.btn = element(by.id('login-btn'));
    this.error = element(by.css('p.error'));

    this.login = function(username, password) {
        var self = this;
        username = username || browser.params.username;
        password = password || browser.params.password;
        return self.username.waitReady().then(function() {
            return self.username.clear();
        }).then(function() {
            return self.username.sendKeys(username);
        }).then(function() {
            return self.password.sendKeys(password);
        }).then(function() {
            return self.btn.click();
        });
    };
}

function IngestProvider() {}

function IngestDashboard() {
    var self = this;
    this.dropDown = element(by.id('ingest-dashboard-dropdown'));
    this.ingestDashboard = element(by.css('.ingest-dashboard-list'));

    this.openDropDown = function() {
        return self.dropDown.click();
    };

    this.getProviderList = function() {
        return self.dropDown.all(by.repeater('item in items'));
    };

    this.getProvider = function(index) {
        return self.getProviderList().get(index);
    };

    this.getProviderButton = function (provider) {
        var toggleButton = provider.element(by.model('item.dashboard_enabled'));
        return toggleButton;
    };

    this.getDashboardList = function() {
        return self.ingestDashboard.all(by.repeater('item in items'));
    };

    this.getDashboard = function(index) {
        return self.getDashboardList().get(index);
    };

    this.getDashboardSettings = function(dashboard) {
        return dashboard.element(by.css('.dropdown'));
    };

    this.getDashboardSettingsStatusButton = function(settings) {
        return settings.element(by.model('item.show_status'));
    };

    this.getDashboardStatus = function(dashboard) {
        return dashboard.element(by.css('.status'));
    };

    this.getDashboardSettingsIngestCountButton = function(settings) {
        return settings.element(by.model('item.show_ingest_count'));
    };

    this.getDashboardIngestCount = function(dashboard) {
        return dashboard.element(by.css('.ingested-count'));
    };
}
