describe('login', function() {
    'use strict';

    function getUrl() {
        return browser.getCurrentUrl().then(function(url) {
            return url.split('#')[1];
        });
    }

    function LoginModal() {
        this.username = element(by.model('username'));
        this.password = element(by.model('password'));
        this.btn = $('#login-btn');

        this.isDisplayed = function() {
            return this.btn.isDisplayed();
        };

        this.login = function(username, password) {
            this.username.clear();
            this.username.sendKeys(username);
            this.password.clear();
            this.password.sendKeys(password);
            this.btn.click();
        };
    }

    var modal;

    beforeEach(function() {
        browser.get('/');
        browser.executeScript('sessionStorage.clear();localStorage.clear();');
        modal = new LoginModal();
    });

    it('renders modal on load', function() {
        expect(modal.isDisplayed()).toBe(true);
    });

    it('can login', function() {
        modal.login('admin', 'admin');
        expect(modal.isDisplayed()).toBe(false);
        expect(getUrl()).toBe('/dashboard');
        expect(element(by.binding('UserName')).getText()).toContain('john');
    });

    it('can logout', function() {
        modal.login('admin', 'admin');
        element(by.binding('UserName')).click();
        element(by.buttonText('Sign out')).click();
        expect(modal.btn.isDisplayed()).toBe(true);
        expect(modal.username.isDisplayed()).toBe(true);
        expect(modal.username.getAttribute('value')).toBe('john');
    });

    it("can't login with wrong credentials", function() {
        modal.login('admin', 'wrongpass');
        expect(modal.isDisplayed()).toBe(true);
        expect(element(by.css('p.error[ng-show="loginError"]')).getText()).toBe('Oops! Invalid Username or Password. Please try again.');
    });
});
