describe('superdesk.auth', function() {
    'use strict';

    function getUrl() {
        return browser.getCurrentUrl().then(function(url) {
            return url.split('#')[1];
        });
    }

    function LoginModal() {
        var modal = element(by.id('login-form')),
            usernameInput = element(by.model('username')),
            passwordInput = element(by.model('password')),
            btn = element(by.id('login-button'));

        this.isDisplayed = function() {
            return modal.isDisplayed();
        };

        this.login = function(username, password) {
            usernameInput.sendKeys(username);
            passwordInput.sendKeys(password);
            btn.click();
        };
    }

    describe('login', function() {
        var modal;

        beforeEach(function() {
            browser.get('');
            modal = new LoginModal();
        });

        it('should be displayed on start', function() {
            expect(modal.isDisplayed()).toBe(true);
        });

        it('should be possible to login', function() {
            modal.login('admin', 'admin');
            expect(getUrl()).toBe('/dashboard');
            expect(modal.isDisplayed()).toBe(false);
        });
    });
});
