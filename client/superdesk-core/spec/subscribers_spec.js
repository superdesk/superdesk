var openUrl = require('./helpers/utils').open,
    subscribers = require('./helpers/subscribers');

describe('subscribers', function() {
    'use strict';

    describe('list subscriber', function() {
        beforeEach(function() {
            openUrl('/#/settings/publish');
        });

        it('list subscriber', function() {
            expect(subscribers.getCount()).toBe(1);

            expect(subscribers.getSubscriber('Public API').count()).toBe(1);
        });
    });

    describe('edit subscriber', function() {
        beforeEach(function() {
            openUrl('/#/settings/publish');
        });

        it('save button is disabled when subscriber type is changed', function() {
            subscribers.edit('Public API');

            expect(subscribers.saveSubscriberButton.isEnabled()).toBe(true);
            subscribers.setType('wire');
            expect(subscribers.saveSubscriberButton.isEnabled()).toBe(false);

            subscribers.cancel();
        });
    });
});
