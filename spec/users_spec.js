
var post = require('./helpers/fixtures').post;
var openUrl = require('./helpers/utils').open;

var ptor = protractor.getInstance();

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
            element.all(by.repeater('user in users')).then(function(users) {
                expect(users.length).toBe(2);
            });

            expect(element(by.repeater('user in users').row(0).column('username')).getText()).toBe('admin');
        });

        it('can delete user', function() {
            var user = element.all(by.repeater('user')),
                activity = element.all(by.repeater('activity'));

            expect(activity.count()).toBe(2);
            user.get(1).click();

            expect($('.preview-pane').evaluate('selected.user')).not.toBe(null);

            var deleteButton = activity.get(1);
            ptor.actions()
                .mouseMove(deleteButton)
                .perform();
            deleteButton.click();

            expect(element(by.binding('bodyText')).getText())
                .toBe('Please confirm you want to delete a user.');
            element(by.buttonText('OK')).click();

            expect(element.all(by.repeater('user')).count()).toBe(1);
            expect($('.preview-pane').evaluate('selected.user')).toBe(null);
        });
    });

    describe('user detail:', function() {
        beforeEach(openUrl('/#/users'));

        it('can open user detail', function() {
            element(by.repeater('user in users').row(0).column('username')).click();
            expect(modelValue('user.display_name')).toBe('first name last name');
            $('#open-user-profile').click();
            expect($('.page-nav-title').getText()).toBe('Users Profile: first name last name');
        });

    });

    describe('user edit:', function() {
        beforeEach(function(done) {
            openUrl('/#/users/')();
            element(by.repeater('user in users').row(1).column('username')).click();
            $('#open-user-profile').click();
            done();
        });

        it('can enable/disable buttons based on form status', function() {
            var buttonSave = element(by.id('save-edit-btn'));
            var buttonCancel = element(by.id('cancel-edit-btn'));
            var inputFirstName = element(by.model('user.first_name'));

            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);

            inputFirstName.sendKeys('X');
            expect(inputFirstName.getAttribute('value')).toBe('fooX');

            expect(buttonSave.isEnabled()).toBe(true);
            expect(buttonCancel.isEnabled()).toBe(true);

            inputFirstName.clear();
            inputFirstName.sendKeys('foo');
            expect(inputFirstName.getAttribute('value')).toBe('foo');

            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);
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
