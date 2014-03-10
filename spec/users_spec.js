describe('users app', function() {
    'use strict';

    function login() {
        element(by.id('login-btn')).isDisplayed().then(function(needLogin) {
            if (needLogin) {
                element(by.model('username')).sendKeys('admin');
                element(by.model('password')).sendKeys('admin');
                element(by.id('login-btn')).click();
            }
        });
    }

    function open(url) {
        return function() {
            browser.get(url);
            login();
        };
    }

    describe('profile', function() {

        beforeEach(open('/#/profile'));

        it('can render user profile', function() {
            expect($('img[sd-user-picture').getAttribute('src')).toBe('http://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?s=200');
            expect(bindingValue('{{ user.UserName }}')).toBe('john');
            expect(modelValue('user.FirstName')).toBe('John');
            expect(modelValue('user.LastName')).toBe('Doe');
            expect(modelValue('user.EMail')).toBe('john.doe@email.com');
            expect(modelValue('user.PhoneNumber')).toBe('0123456789');
        });
    });

    describe('users', function() {
        beforeEach(open('/#/users'));

        it('can list users', function() {
            element.all(by.repeater('user in users')).then(function(users) {
                expect(users.length).toBe(2);
            });

            expect(element(by.repeater('user in users').row(0).column('UserName')).getText()).toBe('john');
        });
    });

    function bindingValue(binding) {
        return element(by.binding(binding)).getText();
    }

    function modelValue(model) {
        return element(by.model(model)).getAttribute('value');
    }

});
