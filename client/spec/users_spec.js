
var post = require('./helpers/fixtures').post;
var openUrl = require('./helpers/utils').open;

describe('USERS', function() {
    'use strict';

    beforeEach(function(done) {
        post({
            uri: '/users',
            json: {
                'first_name': 'foo',
                'last_name': 'bar',
                'username': 'spam',
                'email': 'foo@bar.com'
            }
        }, done);
    });

    describe('profile:', function() {

        beforeEach(openUrl('/#/profile'));

        it('can render user profile', function() {
            expect(bindingValue('user.username')).toBe('admin');
            expect(modelValue('user.first_name')).toBe('first name');
            expect(modelValue('user.last_name')).toBe('last name');
            expect(modelValue('user.email')).toBe('a@a.com');
        });
    });

    describe('users list:', function() {
        beforeEach(openUrl('/#/users'));

        it('can list users', function() {
            expect(element.all(by.repeater('user in users')).count()).toBe(3);
            expect(element(by.repeater('user in users').row(0).column('username')).getText()).toBe('test_user');
        });

        it('can delete user', function() {
            var user = element.all(by.repeater('users')).first(),
                activity = user.all(by.repeater('activities')).first();

            user.click();
            expect($('.preview-pane').evaluate('selected.user')).not.toBe(null);

            browser.actions()
                .mouseMove(activity)
                .perform();
            activity.click();

            var modal = element(by.css('.modal-dialog'));
            expect(modal.element(by.binding('bodyText')).getText())
                .toBe('Please confirm you want to delete a user.');
            modal.element(by.partialButtonText('OK')).click();

            expect(element.all(by.repeater('users')).count()).toBe(2);
        });
    });

    describe('user detail:', function() {
        beforeEach(openUrl('/#/users'));

        it('can open user detail', function() {
            element.all(by.repeater('users')).first().click();
            expect(modelValue('user.display_name')).toBe('first name last name');
            $('#open-user-profile').click();
            expect($('.page-nav-title').getText()).toBe('Users Profile: first name last name');
        });

    });

    describe('user edit:', function() {
        beforeEach(openUrl('/#/users'));
        beforeEach(function() {
            element(by.repeater('user in users').row(1).column('username')).click();
            $('#open-user-profile').click();
        });

        it('can enable/disable buttons based on form status', function() {
            var buttonSave = element(by.id('save-edit-btn'));
            var buttonCancel = element(by.id('cancel-edit-btn'));
            var inputFirstName = element(by.model('user.first_name'));

            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);

            inputFirstName.sendKeys('X');
            expect(inputFirstName.getAttribute('value')).toBe('first nameX');

            expect(buttonSave.isEnabled()).toBe(true);
            expect(buttonCancel.isEnabled()).toBe(true);

            inputFirstName.clear();
            inputFirstName.sendKeys('first name');
            expect(inputFirstName.getAttribute('value')).toBe('first name');

            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);
        });
    });

    function bindingValue(binding) {
        return element(by.binding(binding)).getText();
    }

    function modelValue(model) {
        return element(by.model(model)).getAttribute('value');
    }

});
