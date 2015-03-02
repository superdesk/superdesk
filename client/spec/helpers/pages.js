
'use strict';

exports.login = LoginModal;
exports.workspace = new Workspace();
exports.content = new Content();
exports.editArticle = new EditArticle();

function LoginModal() {
    this.username = element(by.model('username'));
    this.password = element(by.model('password'));
    this.btn = element(by.id('login-btn'));
    this.error = element(by.css('p.error'));

    this.login = function(username, password) {
        username = username || browser.params.username;
        password = password || browser.params.password;
        this.username.clear();
        this.username.sendKeys(username);
        this.password.sendKeys(password);
        return this.btn.click();
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

		browser.wait(function() {
			return selectedDesk.isPresent();
		});

		selectedDesk.getText().then(function(text) {
			if (text.toUpperCase() !== desk.toUpperCase()) {
				selectedDesk.click();
				if (desk.toUpperCase() === 'PERSONAL') {
					personal.click();
				} else {
			    	getDesk(desk).click();
				}
			}
		});
    };
}

function Content() {
    this.setListView = function() {
    	var list = element(by.css('[title="switch to list view"]'));
    	list.isDisplayed().then(function(isVisible) {
            if (isVisible) {
            	list.click();
            }
        });
    };
    this.setGridView = function() {
    	var grid = element(by.css('[title="switch to grid view"]'));
    	grid.then(function(isVisible) {
            if (isVisible) {
            	grid.click();
            }
        });
    };
    this.getItem = function(item) {
    	return element.all(by.repeater('items._items')).get(item);
    };
    this.actionOnItem = function(action, item) {
    	var crtItem = this.getItem(item);
    	browser.actions().mouseMove(crtItem).perform();
    	crtItem.element(by.css('[title="' + action + '"]')).click();
    };
    this.checkMarkedForHighlight = function(highlight, item) {
    	var crtItem = this.getItem(item);
    	expect(crtItem.element(by.className('icon-star-color')).isDisplayed()).toBeTruthy();
    	expect(crtItem.element(by.className('icon-star-color')).getAttribute('tooltip')).toContain(highlight);
    };
}

function EditArticle() {
    this.markAction = function() {
    	element(by.className('svg-icon-add-to-list')).click();
    };
    this.closeAction = function() {
    	element(by.css('[ng-click="close()"]')).click();
    };
}
