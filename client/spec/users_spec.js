
var post = require('./helpers/fixtures').post;
var openUrl = require('./helpers/utils').open;

describe('Users', function() {
    'use strict';

    beforeEach(function(done) {
        post({
            uri: '/users',
            json: {
                'first_name': 'foo',
                'last_name': 'bar',
                'username': 'spam',
                'email': 'foo@bar.com',
                'sign_off': 'foobar'
            }
        }, done);
    });

    describe('profile:', function() {

        beforeEach(function(done) {
            openUrl('/#/profile').then(done);
        });

        it('can render user profile', function() {
            expect(bindingValue('user.username')).toBe('admin');
            expect(modelValue('user.first_name')).toBe('first name');
            expect(modelValue('user.last_name')).toBe('last name');
            expect(modelValue('user.email')).toBe('a@a.com');
            expect(modelValue('user.sign_off')).toBe('');
        });
    });

    describe('users list:', function() {
        beforeEach(function() {
            openUrl('/#/users');
        });

        it('can list users', function() {
            expect(element.all(by.repeater('user in users')).count()).toBe(6);
            expect(element(by.repeater('user in users').row(0).column('username')).getText())
                .toBe('test_user');
        });

        it('list online users', function() {
            element(by.id('online_users')).click();
            expect(element.all(by.repeater('user in users')).count()).toBe(2);
            expect(element(by.repeater('user in users').row(0).column('username')).getText())
                .toBe('test_user');
            expect(element(by.repeater('user in users').row(1).column('username')).getText())
                .toBe('admin');
        });

        xit('can disable user', function() {
            var user = element.all(by.repeater('users')).first(),
                activity = user.element(by.className('icon-trash'));

            user.waitReady()
                .then(function(elem) {
                    return browser.actions().mouseMove(elem).perform();
                })
                .then(function() {
                    activity.waitReady().then(function(elem) {
                        elem.click();
                    });
                });

            element(by.css('.modal-dialog')).waitReady().then(function(elem) {
                browser.wait(function() {
                    return elem.element(by.binding('bodyText'))
                        .getText()
                        .then(function(text) {
                            if (text === 'Please confirm that you want to disable a user.') {
                                return true;
                            }
                        });
                }, 5000);
                return elem;
            }).then(function(elem) {
                browser.wait(function() {
                    try {
                        return elem.element(by.partialButtonText('OK'))
                            .click()
                            .then(function() {
                                return true;
                            });
                    } catch (err) {
                        console.log(err);
                    }
                }, 5000);
            }).then(function() {
                browser.wait(function() {
                    return element.all(by.repeater('users'))
                        .count()
                        .then(function(c) {
                            if (c === 3) {
                                return true;
                            }
                        });
                }, 5000);
            });
        });
    });

    describe('user detail:', function() {
        beforeEach(function(done) {
            openUrl('/#/users').then(done);
        });

        it('can open user detail', function() {
            element.all(by.repeater('users')).first().click();
            expect(modelValue('user.display_name'))
                .toBe('first name last name');
            $('#open-user-profile').waitReady()
                .then(function(elem) {
                    elem.click();
                });
            var pageNavTitle = $('.page-nav-title');
            browser.wait(function() {
                return pageNavTitle.getText().then(function(text) {
                    if (text.indexOf('Users Profile') === 0) {
                        return true;
                    }
                });
            }, 2000);
            expect(pageNavTitle.getText())
                .toBe('Users Profile: first name last name');
        });

    });

    describe('user edit:', function() {
        beforeEach(function(done) {
            openUrl('/#/users').then(function() {
                return element(by.repeater('user in users').row(0).column('username'))
                    .waitReady();
            }).then(function(elem) {
                return elem.click();
            }).then(function() {
                return $('#open-user-profile').waitReady();
            }).then(function(elem) {
                return elem.click();
            }).then(done);
        });

        it('can enable/disable buttons based on form status', function() {
            var buttonSave = element(by.id('save-edit-btn'));
            var buttonCancel = element(by.id('cancel-edit-btn'));
            var inputFirstName = element(by.model('user.first_name'));
            var inputSignOff = element(by.model('user.sign_off'));

            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);

            inputSignOff.sendKeys('X');
            expect(inputSignOff.getAttribute('value')).toBe('X');

            browser.sleep(200);
            expect(buttonSave.isEnabled()).toBe(true);
            expect(buttonCancel.isEnabled()).toBe(true);

            inputFirstName.clear();
            inputSignOff.clear();
            inputFirstName.sendKeys('first name');
            expect(inputFirstName.getAttribute('value')).toBe('first name');

            browser.sleep(200);
            expect(buttonSave.isEnabled()).toBe(false);
            expect(buttonCancel.isEnabled()).toBe(false);
        });
    });

    describe('default desk field should not be visible', function() {
        beforeEach(function(done) {
            openUrl('/#/users').then(done);
        });

        it('while creating a new user', function() {
            var buttonCreate = element(by.className('sd-create-btn'));

            buttonCreate.click();
            expect(browser.driver.isElementPresent(by.id('user_default_desk'))).toBe(false);
        });

        it('while pre-viewing and user clicks on create new user', function() {
            var buttonCreate = element(by.className('sd-create-btn'));
            element.all(by.repeater('users')).first().click();

            buttonCreate.click();
            expect(browser.driver.isElementPresent(by.id('user_default_desk'))).toBe(false);
        });
    });

    function bindingValue(binding) {
        return element(by.binding(binding)).getText();
    }

    function modelValue(model) {
        return element(by.model(model)).getAttribute('value');
    }

});
