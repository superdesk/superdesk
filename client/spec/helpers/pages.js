
'use strict';

exports.login = LoginModal;
exports.workspace = new Workspace();

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

    function switchDesk(toPersonal) {

        var selectedDesk = element(by.id('selected-desk'));

        browser.wait(function() {
            return selectedDesk.isPresent();
        });

        selectedDesk.getText().then(function(text) {
            var isPersonal = text === 'PERSONAL';
            if (isPersonal !== toPersonal) {
                selectedDesk.click();
                element(by.id('select-desk-menu')).all(by.tagName('button')).last().click();
            }
        });
    }

    this.openPersonal = function() {
        return switchDesk(true);
    };

    this.openDesk = function() {
        return switchDesk(false);
    };
}
