'use strict';

exports.login = LoginModal;
exports.workspace = new Workspace();
exports.content = new Content();
exports.authoring = new Authoring();
exports.ingestProvider = new IngestProvider();
exports.ingestDashboard = new IngestDashboard();
exports.masterDesks = new MasterDesks();

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

function Workspace() {
    this.getDesk = function(name) {
        var desks = element.all(by.repeater('desk in userDesks'));
        return desks.all(by.css('[option="' + name.toUpperCase() + '"]'));
    };

    this.switchToDesk = function(desk) {
        var selectedDesk = element(by.id('selected-desk'));
        var personal = element(by.css('[option="PERSONAL"]'));
        var getDesk = this.getDesk;

        return selectedDesk.waitReady().then(function(elem) {
            return elem.getText();
        }).then(function(text) {
            if (text.toUpperCase() !== desk.toUpperCase()) {
                selectedDesk.click();
                if (desk.toUpperCase() === 'PERSONAL') {
                    return personal.click();
                } else {
                    return getDesk(desk).click();
                }
            }
        });
    };
}

function Content() {
    this.setListView = function() {
        var list = element(by.css('[title="switch to list view"]'));
        return list.isDisplayed().then(function(isVisible) {
            if (isVisible) {
                list.click();
            }
        });
    };
    this.setGridView = function() {
        var grid = element(by.css('[title="switch to grid view"]'));
        return grid.then(function(isVisible) {
            if (isVisible) {
                grid.click();
            }
        });
    };
    this.getItem = function(item) {
        return element.all(by.repeater('items._items')).get(item);
    };
    this.actionOnItem = function(action, item) {
        var crtItem;
        return this.getItem(item)
            .waitReady().then(function(elem) {
                crtItem = elem;
                return browser.actions().mouseMove(crtItem).perform();
            }).then(function() {
                return crtItem
                    .element(by.css('[title="' + action + '"]'))
                    .click();
            });
    };
}

function Authoring() {
    this.markAction = function() {
        return element(by.className('svg-icon-add-to-list')).click();
    };
    this.close = function() {
        return element(by.css('[ng-click="close()"]')).click();
    };
    this.save = function() {
        return element(by.css('[ng-click="save(item)"]')).click();
    };
    this.showSearch = function() {
        return element(by.id('Search')).click();
    };
    this.showVersions = function() {
        return element(by.css('[title="Versions"]')).click();
    };

    this.getSearchItem = function(item) {
        return element.all(by.repeater('pitem in contentItems')).get(item);
    };
    this.addToGroup = function(item, group) {
        var crtItem = this.getSearchItem(item);
        browser.actions().mouseMove(crtItem).perform();
        crtItem.element(by.css('[title="Add to package"]')).click();
        var groups = crtItem.all(by.repeater('t in groupList'));
        return groups.all(by.css('[option="' + group.toUpperCase() + '"]')).click();
    };
    this.addMultiToGroup = function(group) {
        return element.all(by.css('[class="icon-package-plus"]')).first()
            .waitReady()
            .then(function(elem) {
                return elem.click();
            }).then(function() {
                var groups = element(by.repeater('t in groupList'));
                return groups.all(by.css('[option="' + group.toUpperCase() + '"]'))
                    .click();
            });
    };
    this.getGroupItems = function(group) {
        return element(by.id(group.toUpperCase())).all(by.repeater('item in group.items'));
    };
    this.getGroupItem = function(group, item) {
        return this.getGroupItems(group).get(item);
    };
    this.moveToGroup = function(srcGroup, scrItem, dstGroup, dstItem) {
        var src = this.getGroupItem(srcGroup, scrItem).element(by.css('[class="info"]'));
        var dst = this.getGroupItem(dstGroup, dstItem).element(by.css('[class="info"]'));
        return src.waitReady().then(function() {
            browser.actions()
                .mouseMove(src, {x: 0, y: 0})
                .mouseDown()
                .perform()
                .then(function() {
                    dst.waitReady().then(function () {
                        browser.actions()
                            .mouseMove(dst, {x: 0, y: 0})
                            .mouseUp()
                            .perform();
                    });
                });
        });
    };
    this.selectSearchItem = function(item) {
      var crtItem = this.getSearchItem(item);
      var icon = crtItem.element(by.tagName('i'));
      return icon.waitReady().then(function() {
          browser.actions()
              .mouseMove(icon)
              .perform();
      }).then(function() {
          crtItem.element(by.css('[ng-click="addToSelected(pitem)"]')).click();
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

function MasterDesks() {
    this.switchToTab = function(name) {
        element(by.id(name)).click();
    };

    this.getDesk = function(desk) {
    	return element.all(by.repeater('desk in desks._items')).get(desk);
    };

    this.getRole = function(desk, role) {
    	return this.getDesk(desk).all(by.repeater('role in roles')).get(role);
    };

    this.getUser = function(desk, role, user) {
    	return this.getRole(desk, role).all(by.repeater('item in items')).get(user);
    };

    this.goToDesk = function(desk) {
    	this.getDesk(desk).element(by.className('icon-external')).click();
    };

    this.editDesk = function(desk) {
    	this.getDesk(desk).element(by.className('icon-dots')).click();
    	this.getDesk(desk).element(by.className('icon-pencil')).click();
    };
}
