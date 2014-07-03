define([
    'angular',
    'require',
    'lodash',
    './controllers/main',
    './directives'
], function(angular, require, _) {
    'use strict';

    var app = angular.module('superdesk.planning', [
        'superdesk.planning.directives'
    ]);

    return app
        .value('mockDataExample', {
            list: ['array1', 'array2', 'array3'],
            name: 'sample name'
        })
        .config(['superdeskProvider', function(superdesk) {
            superdesk
                .activity('/planning/', {
                    label: gettext('Planning'),
                    priority: 100,
                    beta: true,
                    controller: require('./controllers/main'),
                    templateUrl: 'scripts/superdesk-planning/views/main.html',
                    category: superdesk.MENU_MAIN,
                    reloadOnSearch: false,
                    filters: []
                });
        }])
        .service('userDesks', ['api', 'storage', function(api, storage) {
            return {
                currentDeskId: null,
                desks: null,
                getDesks: function(user) {
                    var self = this;
                    return api.users.getByUrl(user._links.self.href + '/desks')
                    .then(function(result) {
                        self.desks = result;
                        return result;
                    });
                },
                getCurrentDesk: function() {
                    this.currentDeskId = storage.getItem('planning:currentDeskId') || null;
                    return _.find(this.desks._items, {_id: this.currentDeskId});
                },
                setCurrentDesk: function(desk) {
                    this.currentDeskId = desk._id;
                    storage.setItem('planning:currentDeskId', this.currentDeskId);
                }
            };
        }]);
});
