'use strict';

var monitoring = require('./helpers/monitoring'),
    publishQueue = require('./helpers/publish_queue');

describe('publish queue', function() {
    it('publish using HTTP Push delivery type', function() {
        monitoring.openMonitoring();
        monitoring.openAction(1, 0);
        monitoring.openSendMenu();
        monitoring.publish();
        publishQueue.openPublishQueue();
        expect(publishQueue.getHeadline(0).getText()).toMatch(/item5/);
        expect(publishQueue.getDestination(0).getText()).toMatch(/HTTP Push/);
    });
});
