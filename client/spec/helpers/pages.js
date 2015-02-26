
'use strict';

exports.login = LoginModal;
exports.workspace = new Workspace();

function LoginModal() {
    this.username = element(by.model('username'));
    this.password = element(by.model('password'));
    this.btn = element(by.css('#login-btn'));
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
        element(by.buttonText('PERSONAL')).isDisplayed().then(function(isPersonal) {
            if (isPersonal && !toPersonal) {
                element(by.partialButtonText('PERSONAL')).click();
                element(by.partialButtonText('SPORTS DESK')).click();
                console.log('switching to desk');
            } else if (!isPersonal && toPersonal) {
                element(by.partialButtonText('SPORTS DESK')).click();
                element(by.partialButtonText('PERSONAL')).click();
                console.log('switching to personal');
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
