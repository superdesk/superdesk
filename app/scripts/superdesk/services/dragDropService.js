define(['angular'], function(angular) {
    'use strict';

    angular.module('superdesk.services').
        service('dragDropService', [function() {
            this.item = null;
        }]);
});
