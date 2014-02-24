describe('login', function() {
    'use strict';

    function getUrl() {
        return browser.getCurrentUrl().then(function(url) {
            return url.split('#')[1];
        });
    }

    function LoginModal() {
        var usernameInput = element(by.model('username')),
            passwordInput = element(by.model('password')),
            btn = element(by.id('login-button'));

        this.isDisplayed = function() {
            browser.sleep(1000); // wait for modal animation to complete
            return usernameInput.isDisplayed();
        };

        this.login = function(username, password) {
            usernameInput.sendKeys(username);
            passwordInput.sendKeys(password);
            btn.click();
        };
    }

    describe('login modal', function() {
        var modal;

        beforeEach(function() {
            browser.get('/');
            modal = new LoginModal();
        });

        it('should be visible on load', function() {
            expect(modal.isDisplayed()).toBe(true);
        });

        it('should be possible to login', function() {
            modal.login('admin', 'admin');
            expect(modal.isDisplayed()).toBe(false);
            expect(getUrl()).toBe('/dashboard');
            expect(element(by.tagName('body')).evaluate('identity.UserName')).toBe('john');
        });
    });
});
