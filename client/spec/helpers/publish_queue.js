
'use strict';

var openUrl = require('./utils').open;
module.exports = new PublishQueue();

function PublishQueue() {

    this.openPublishQueue = function() {
        openUrl('/#/publish_queue');
    };

    this.getRow = function(rowNo) {
        return element.all(by.css('[ng-click="preview(queue_item);"]')).get(rowNo);
    };

    this.getHeadline = function(rowNo) {
        var row = this.getRow(rowNo);
        return row.all(by.className('ng-binding')).get(2);
    };

    this.getDestination = function(rowNo) {
        var row = this.getRow(rowNo);
        return row.all(by.className('ng-binding')).get(6);
    };
}
