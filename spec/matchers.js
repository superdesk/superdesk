'use strict';

/* global jasmine */

beforeEach(function() {
    this.addMatchers({
        // check if elem is displayed
        toBeDisplayed: function() {
            var spec = this;
            this.actual.getText().then(function(elem) {
                spec.message = function() {
                    return [
                        'Expected ' + jasmine.pp(elem) + ' to be Displayed.',
                        'Expected ' + jasmine.pp(elem) + ' not to be Displayed.'
                    ];
                };
            });

            return this.actual.isDisplayed().then(function(isDisplayed) {
                return isDisplayed === true;
            });
        }
    });
});
