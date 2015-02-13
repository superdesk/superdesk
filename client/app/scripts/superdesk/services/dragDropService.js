define(['angular'], function(angular) {
    'use strict';

    return angular.module('superdesk.services.dragdrop', []).
        service('dragDropService', [function() {
            this.item = null;
        }]);
});
