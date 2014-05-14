
var openUrl = require('./utils').open;

describe('USERS', function() {
    'use strict';

    describe('profile:', function() {

        beforeEach(openUrl('/#/profile'));

        it('can render user profile', function() {
            expect($('img[sd-user-picture').getAttribute('src')).toBe('https://avatars.githubusercontent.com/u/275305');
            expect(bindingValue('{{ user.username }}')).toBe('john');
            expect(modelValue('user.first_name')).toBe('John');
            expect(modelValue('user.last_name')).toBe('Doe');
            expect(modelValue('user.email')).toBe('john.doe@email.com');
            //expect(modelValue('user.phone')).toBe('0123456789');
        });
    });

    describe('users list:', function() {
        beforeEach(openUrl('/#/users'));

        it('can list users', function() {
            element.all(by.repeater('user in users')).then(function(users) {
                expect(users.length).toBe(2);
            });

            expect(element(by.repeater('user in users').row(0).column('username')).getText()).toBe('john');
        });

        it('can delete user', function() {
            var user = element.all(by.repeater('user')),
                activity = element.all(by.repeater('activity'));

            expect(activity.count()).toBe(2);
            user.first().click();

            expect($('.preview-pane').evaluate('selected.user')).not.toBe(null);

            activity.first().click();

            expect(element(by.binding('{{bodyText}}')).getText())
                .toBe('Please confirm you want to delete a user.');
            element(by.buttonText('OK')).click();

            // it reloads the list after delete which will on apiary return 2 items again..
            expect(element.all(by.repeater('user')).count()).toBe(2);

            // but there should be no preview
            expect($('.preview-pane').evaluate('selected.user')).toBe(null);
        });
    });

    describe('user detail:', function() {
        beforeEach(openUrl('/#/users'));

        it('can open user detail', function() {
            element(by.repeater('user in users').row(0).column('username')).click();
            expect(modelValue('user.display_name')).toBe('John Doe');
            $('.preview-pane > .actions > a.btn').click();
            expect(browser.getCurrentUrl()).toBe('http://localhost:9090/#/users/2');
            expect($('.page-nav-title').getText()).toBe('Users Profile: John Doe');
        });

    });

    describe('user edit:', function() {
        beforeEach(openUrl('/#/users/2'));

        it('can enable/disable buttons based on form status', function() {
            var buttonSave = element(by.buttonText('Save'));
            var buttonCancel = element(by.buttonText('Cancel'));
            var inputFirstName = element(by.model('user.first_name'));

            expect(buttonSave.getAttribute('disabled')).toBe('true');
            expect(buttonCancel.getAttribute('disabled')).toBe('true');

            inputFirstName.sendKeys('X');
            expect(inputFirstName.getAttribute('value')).toBe('JohnX');

            expect(buttonSave.getAttribute('disabled')).toBe(null);
            expect(buttonCancel.getAttribute('disabled')).toBe(null);

            inputFirstName.clear();
            inputFirstName.sendKeys('John');
            expect(inputFirstName.getAttribute('value')).toBe('John');

            expect(buttonSave.getAttribute('disabled')).toBe('true');
            expect(buttonCancel.getAttribute('disabled')).toBe('true');
        });

        it('can validate phone number', function() {
            var input = element(by.model('user.phone')),
                msg = $('[ng-show^="userForm.phone.$error"]');

            expect(msg.isDisplayed()).toBe(false);

            input.clear();
            expect(input.getAttribute('value')).toBe('');

            expect(msg.isDisplayed()).toBe(false);

            input.sendKeys('1234');
            expect(input.getAttribute('value')).toBe('1234');

            expect(msg.isDisplayed()).toBe(true);

            input.clear();
            expect(input.getAttribute('value')).toBe('');

            expect(msg.isDisplayed()).toBe(false);
        });
    });

    function bindingValue(binding) {
        return element(by.binding(binding)).getText();
    }

    function modelValue(model) {
        return element(by.model(model)).getAttribute('value');
    }

});
