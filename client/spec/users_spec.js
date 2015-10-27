
var authoring = require('./helpers/authoring'),
    openUrl = require('./helpers/utils').open,
    post = require('./helpers/fixtures').post,
    userPrefs = require('./helpers/user_prefs'),
    workspace = require('./helpers/workspace');

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
            expect(modelValue('user.sign_off')).toBe('fl');
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

            inputSignOff.clear();
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
            expect(buttonCancel.isEnabled()).toBe(true);
        });
    });

    describe('editing user preferences:', function () {
        beforeEach(function(done) {
            userPrefs.navigateTo().then(function () {
                return userPrefs.prefsTab.click();
            }).then(done);
        });

        it('should filter categories in the Authoring metadata head menu ' +
           'based on the user\'s preferred categories settings',
            function () {
                var catListItems,  // elements in the offered category list
                    parentDiv;

                userPrefs.btnCheckNone.click();  // uncheck all categories

                // select the Entertainment and Finance categories
                userPrefs.categoryCheckboxes.get(3).click();  // Entertainment
                userPrefs.categoryCheckboxes.get(4).click();  // Finance

                userPrefs.btnSave.click();  // save changes

                // navigate to Workspace and create a new article
                workspace.openContent();
                authoring.navbarMenuBtn.click();
                authoring.newPlainArticleLink.click();

                // authoring opened, click the set category menu and see what
                // categories are offered
                authoring.setCategoryBtn.click();

                // it is difficult to distinguish the categories menu element
                // from other similar menus, thus we need to perform all
                // element selections from the button's immediate parent
                parentDiv = authoring.setCategoryBtn.element(by.xpath('..'));

                /////
                // XXX: workaround - there seems to be a bug in sd-typeahead,
                // no categories are shown, thus something needs to be entered
                // into textbox (and immediately deleted) so that the category
                // list shows up
                /// TODO: remove when the bug is resolved and this is not needed
                //        anymore
                var txtCategory = parentDiv.element(by.css('input[type="text"]'));
                txtCategory.sendKeys('x', protractor.Key.BACK_SPACE);
                /// end workaround ///

                catListItems = parentDiv.all(by.css('.item-list li > button'));

                expect(catListItems.count()).toEqual(2);
                expect(catListItems.get(0).getText()).toEqual('Entertainment');
                expect(catListItems.get(1).getText()).toEqual('Finance');
            }
        );
    });

    describe('editing user privileges:', function () {
        beforeEach(function (done) {
            userPrefs.navigateTo().then(function () {
                return userPrefs.privlTab.click();
            }).then(done);
        });

        it('should reset the form to the last saved state when the Cancel ' +
            'button is clicked',
            function () {
                var checkboxes = userPrefs.privlCheckboxes;

                // Initially all checboxes are unchecked. Now let's select
                // a few of them, click the Cancel button and see if they have
                // been reset.
                checkboxes.get(0).click();  // archive
                checkboxes.get(2).click();  // content filters
                expect(checkboxes.get(0).isSelected()).toBeTruthy();
                expect(checkboxes.get(2).isSelected()).toBeTruthy();

                userPrefs.btnCancel.click();

                expect(checkboxes.get(0).isSelected()).toBeFalsy();
                expect(checkboxes.get(2).isSelected()).toBeFalsy();

                // Check the checkboxes again, save the changes, then check a
                // few more. After clicking the Cancel button, only the
                // checkboxes checked after the save should be reset.
                checkboxes.get(0).click();
                checkboxes.get(2).click();
                expect(checkboxes.get(0).isSelected()).toBeTruthy();
                expect(checkboxes.get(2).isSelected()).toBeTruthy();

                userPrefs.btnSave.click();

                checkboxes.get(1).click();  // archived management
                checkboxes.get(4).click();  // desk management
                expect(checkboxes.get(1).isSelected()).toBeTruthy();
                expect(checkboxes.get(4).isSelected()).toBeTruthy();

                userPrefs.btnCancel.click();

                expect(checkboxes.get(0).isSelected()).toBeTruthy();
                expect(checkboxes.get(2).isSelected()).toBeTruthy();
                expect(checkboxes.get(1).isSelected()).toBeFalsy();
                expect(checkboxes.get(4).isSelected()).toBeFalsy();
            }
        );
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
