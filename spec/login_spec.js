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
            this.username.sendKeys(username);
            this.password.sendKeys(password);
            this.btn.click();
        };
    }

    describe('login', function() {
        var modal;

        beforeEach(function() {
            browser.get('/');
            modal = new LoginModal();
        });

        it('renders modal on load', function() {
            expect(modal.isDisplayed()).toBe(true);
        });

        it('can login', function() {
            modal.login('admin', 'admin');
            expect(modal.isDisplayed()).toBe(false);
            expect(getUrl()).toBe('/dashboard');
            expect(element(by.binding('UserName')).getText()).toBe('john');
        });

        it('can logout', function() {
            var logoutBtn = $('.logout-btn');
            expect(logoutBtn.isDisplayed()).toBe(true);
            logoutBtn.click();
            expect(modal.btn.isDisplayed()).toBe(true);
            expect(modal.username.isDisplayed()).toBe(false); // reuse stored username
        });
    });
});
