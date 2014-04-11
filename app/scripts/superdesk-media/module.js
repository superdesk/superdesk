define([
    'angular',
    'require',
    './controllers/list',
    './controllers/uploadMedia',
    '../superdesk-items-common/module'
], function(angular, require) {
    'use strict';

    var app = angular.module('superdesk.media', ['superdesk.items-common']);

    app.config(['superdeskProvider', function(superdesk) {
        superdesk
            .activity('/media/', {
                label: gettext('Media'),
                priority: 100,
                controller: require('./controllers/list'),
                templateUrl: require.toUrl('./views/list.html'),
                category: superdesk.MENU_MAIN,
                reloadOnSearch: false,
                beta: true
            })
            .activity('edit.media', {
                label: gettext('Upload media'),
                modal: true,
                cssClass: 'upload-media responsive-popup',
                controller: require('./controllers/uploadMedia'),
                templateUrl: require.toUrl('./views/upload-media.html'),
                filters: [
                    {action: 'edit', type: 'media'}
                ]
            });
    }])
    .config(['apiProvider', function(apiProvider) {
        apiProvider.api('media', {
            type: 'mock',
            service: function() {

                this.getName = function() {
                    return this.name;
                };

                var query = this.query;
                this.query = function(criteria) {
                    return query.call(this, criteria);
                };
            },
            backend: {
                data: [
                    {
                        'Id': 1,
                        'href': 'http://superdesk.apiary.io/ItemMedia/1',
                        'ByLine': 'John Doe',
                        'Provider': 'My Company LTD',
                        'MimeType': 'image/jpeg',
                        'Type': 'picture',
                        'CreatedOn': '2013-07-03T10:11:12Z',
                        'Version': '1',
                        'VersionCreated': '2013-07-03T10:11:12Z',
                        'Status': 'public',
                        'FileMeta': {
                            'Manufacturer': 'CANON',
                            'Orientation': 'landscape'
                        },
                        'CopyrightHolder': {'en': 'Sourcefabric o.p.s.'},
                        'CopyrightNotice': {'en': '(c) Copyright Sourcefabric o.p.s. 2014'},
                        'UsageTerms': {'en': 'You are not allowed.'},
                        'Headline': {'en': 'No news today'},
                        'Renditions': {
                            'thumbnail': {
                                'href': 'http://farm4.staticflickr.com/3665/9203816834_3329fac058_q_d.jpg',
                                'Width': 150,
                                'Height': 150
                            },
                            'original': {
                                'href': 'http://farm4.staticflickr.com/3665/9203816834_9f62964627_o_d.jpg',
                                'Width': 5198,
                                'Height': 3462
                            }
                        }
                    }
                ]
            }
        });
    }]);
});
