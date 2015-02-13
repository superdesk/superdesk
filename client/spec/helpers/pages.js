'use strict';

exports.login = LoginModal;
var params = browser.params;

function LoginModal() {
    this.username = element(by.model('username'));
    this.password = element(by.model('password'));
    this.btn = element(by.css('#login-btn'));
    this.error = element(by.css('p.error'));

    this.login = function(username, password) {
        username = username || params.username;
        password = password || params.password;
        this.username.clear();
        this.username.sendKeys(username);
        this.password.sendKeys(password);
        this.btn.click();
    };
}
