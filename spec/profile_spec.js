describe('profile', function() {
    'use strict';

    beforeEach(function() {
        browser.get('/#/profile');
        browser.executeScript('sessionStorage.clear();localStorage.clear();');
        element(by.model('username')).sendKeys('admin');
        element(by.model('password')).sendKeys('admin');
        element(by.id('login-btn')).click();
    });

    it('can render user profile', function() {

        function bindingValue(binding) {
            return element(by.binding(binding)).getText();
        }

        function modelValue(model) {
            return element(by.model(model)).getAttribute('value');
        }

        expect($('img[sd-user-picture').getAttribute('src')).toBe('http://www.gravatar.com/avatar/205e460b479e2e5b48aec07710c08d50?s=200');
        expect(bindingValue('{{ user.UserName }}')).toBe('john');
        expect(modelValue('user.FirstName')).toBe('John');
        expect(modelValue('user.LastName')).toBe('Doe');
        expect(modelValue('user.EMail')).toBe('john.doe@email.com');
        expect(modelValue('user.PhoneNumber')).toBe('0123456789');
    });

});
