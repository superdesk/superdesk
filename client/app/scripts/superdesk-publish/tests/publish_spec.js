'use strict';

describe('publish queue', function() {

    var subscribers = {'_items': [
        {
            '_created': '2015-05-11T06:00:48+0000',
            '_etag': '8d27862ca97a8741aaf8ac38f1de3605e085062c',
            '_id': '555045901d41c80c5804501a',
            '_links': {
                'self': {
                    'href': 'subscribers/555045901d41c80c5804501a',
                    'title': 'Subscriber'
                }
            },
            '_updated': '2015-05-12T01:01:47+0000',
            'destinations': [
                {
                    'config': {
                        'recipients': 'test@aap.com.au'
                    },
                    'delivery_type': 'email',
                    'name': 'test'
                }
            ],
            'is_active': true,
            'name': 'test'
        }
    ]};

    var output_channels = {'_items': [
        {
            '_created': '2015-05-20T04:14:15+0000',
            '_etag': '947ac937ed08ef5679eb48ff3ddef1d0d82bb5fc',
            '_id': '555c0a171d41c83fd826b801',
            '_links': {
                'self': {
                    'href': 'output_channels/555c0a171d41c83fd826b801',
                    'title': 'Output_channel'
                }
            },
            '_updated': '2015-05-20T04:14:15+0000',
            'channel_type': 'address',
            'description': 'Digital',
            'destinations': [
                '555045901d41c80c5804501a'
            ],
            'format': 'nitf',
            'is_active': true,
            'is_digital': true,
            'name': 'Digital',
            'sequence_num_settings': {}
        },
        {
            '_created': '2015-05-11T06:01:19+0000',
            '_etag': 'a508d504362ef67d130597b0553a32dfe4836e24',
            '_id': '555045af1d41c80c593e7656',
            '_links': {
                'self': {
                    'href': 'output_channels/555045af1d41c80c593e7656',
                    'title': 'Output_channel'
                }
            },
            '_updated': '2015-05-11T06:01:26+0000',
            'channel_type': 'address',
            'description': 'Email',
            'destinations': [
                '555045901d41c80c5804501a'
            ],
            'format': 'nitf',
            'is_active': true,
            'name': 'Email',
            'sequence_num_settings': {}
        }
    ]};

    var publish_queue = {'_items': [
            {
            '_created': '2015-05-15T06:27:13+0000',
            '_etag': 'd18bf9f762b03815acc189fdcef633bf67f8e222',
            '_id': '555591c11d41c830e91b1f9f',
            '_links': {
                'self': {
                    'href': 'publish_queue/555591c11d41c830e91b1f9f',
                    'title': 'Publish_queue'
                }
            },
            '_updated': '2015-05-19T04:18:23+0000',
            'completed_at': '2015-05-19T04:18:23+0000',
            'content_type': 'text',
            'destination': {
                'config': {
                    'recipients': 'test@aap.com.au'
                },
                'delivery_type': 'email',
                'name': 'test'
            },
            'formatted_item_id': '555591c11d41c830e91b1f9e',
            'headline': 'RL:Souths win but Dugan stars in NRL',
            'item_id': 'tag:localhost:2015:a613f9b5-c7c4-4980-a3e8-0a90586ba59e',
            'output_channel_id': '555045af1d41c80c593e7656',
            'publish_schedule': null,
            'published_seq_num': 11,
            'publishing_action': 'published',
            'selector_codes': [
                'T12',
                'TTT',
                'XXX'
            ],
            'state': 'success',
            'subscriber_id': '555045901d41c80c5804501a',
            'transmit_started_at': '2015-05-19T04:18:23+0000',
            'unique_name': '#55861'
        },
        {
            '_created': '2015-05-19T05:13:29+0000',
            '_etag': '88602d040ee9e67feb25d928d18325d2f8c24830',
            '_id': '555ac6791d41c8105b514cf0',
            '_links': {
                'self': {
                    'href': 'publish_queue/555ac6791d41c8105b514cf0',
                    'title': 'Publish_queue'
                }
            },
            '_updated': '2015-05-19T05:13:34+0000',
            'completed_at': '2015-05-19T05:13:34+0000',
            'content_type': 'text',
            'destination': {
                'config': {
                    'recipients': 'test@aap.com.au'
                },
                'delivery_type': 'email',
                'name': 'test'
            },
            'formatted_item_id': '555ac6791d41c8105b514cef',
            'headline': 'Angle Park Greyhound NSW TAB Divs 1-8 Monday',
            'item_id': 'tag:localhost:2015:15982dd3-0ab2-4da1-b2a2-b8f322e8a612',
            'output_channel_id': '555045af1d41c80c593e7656',
            'publish_schedule': null,
            'published_seq_num': 15,
            'publishing_action': 'corrected',
            'selector_codes': [
                'TTT',
                'XXX',
                'T12'
            ],
            'state': 'success',
            'subscriber_id': '555045901d41c80c5804501a',
            'transmit_started_at': '2015-05-19T05:13:34+0000',
            'unique_name': '#55860'
        },
        {
            '_created': '2015-05-19T08:56:43+0000',
            '_etag': '3cd58463412d08d2d776a931f04f997282025e7a',
            '_id': '555afacb1d41c817984405b5',
            '_links': {
                'self': {
                    'href': 'publish_queue/555afacb1d41c817984405b5',
                    'title': 'Publish_queue'
                }
            },
            '_updated': '2015-05-19T08:56:49+0000',
            'completed_at': '2015-05-19T08:56:49+0000',
            'content_type': 'text',
            'destination': {
                'config': {
                    'recipients': 'test@aap.com.au'
                },
                'delivery_type': 'email',
                'name': 'test'
            },
            'formatted_item_id': '555afacb1d41c817984405b4',
            'headline': 'NSW:Man quizzed over suspicious Sydney death',
            'item_id': 'tag:localhost:2015:7466da05-56d2-47d4-a401-b79ed2af08a2',
            'output_channel_id': '555045af1d41c80c593e7656',
            'publish_schedule': null,
            'published_seq_num': 16,
            'publishing_action': 'published',
            'selector_codes': [
                'XXX',
                'TTT',
                'T12'
            ],
            'state': 'success',
            'subscriber_id': '555045901d41c80c5804501a',
            'transmit_started_at': '2015-05-19T08:56:49+0000',
            'unique_name': '#57537'
        }
    ]};

    var $scope, controller;

    beforeEach(module('superdesk.authoring'));
    beforeEach(module('superdesk.users'));
    beforeEach(module('superdesk.publish'));
    beforeEach(module('superdesk.mocks'));

    beforeEach(inject(function($rootScope, $controller, adminPublishSettingsService, $q, api) {
        spyOn(adminPublishSettingsService, 'fetchSubscribers').and.returnValue($q.when(subscribers));
        spyOn(adminPublishSettingsService, 'fetchOutputChannels').and.returnValue($q.when(output_channels));
        spyOn(api.publish_queue, 'query').and.returnValue($q.when(publish_queue));
        $scope = $rootScope.$new();
        controller = $controller('publishQueueCtrl',
            {
                $scope: $scope,
                'adminPublishSettingsService': adminPublishSettingsService,
                '$q': $q,
                'api': api
            }
        );
    }));

    it('can load items from publish_queue', inject(function($rootScope) {
        $rootScope.$digest();
        expect($scope.publish_queue.length).toBe(3);
        _.each($scope.publish_queue, function(item) {
            expect(item.selected).toBe(false);
        });
        expect($scope.showResendBtn).toBe(false);
        expect($scope.showCancelBtn).toBe(false);
    }));

    it('can select multiple queue items', inject(function($rootScope) {
        $rootScope.$digest();
        expect($scope.publish_queue.length).toBe(3);
        $scope.publish_queue[0].selected = true;
        $scope.selectQueuedItem($scope.publish_queue[0]);
        expect($scope.multiSelectCount).toBe(1);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
        $scope.publish_queue[1].selected = true;
        $scope.selectQueuedItem($scope.publish_queue[1]);
        expect($scope.multiSelectCount).toBe(2);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
    }));

    it('can deselect queue items', inject(function($rootScope) {
        $rootScope.$digest();
        expect($scope.publish_queue.length).toBe(3);
        $scope.publish_queue[0].selected = true;
        $scope.publish_queue[1].selected = true;
        $scope.selectQueuedItem($scope.publish_queue[0]);
        $scope.selectQueuedItem($scope.publish_queue[1]);
        expect($scope.multiSelectCount).toBe(2);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
        $scope.publish_queue[1].selected = false;
        $scope.selectQueuedItem($scope.publish_queue[1]);
        expect($scope.multiSelectCount).toBe(1);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
        $scope.publish_queue[0].selected = false;
        $scope.selectQueuedItem($scope.publish_queue[0]);
        expect($scope.multiSelectCount).toBe(0);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
    }));

    it('can deselect all queue items', inject(function($rootScope) {
        $rootScope.$digest();
        expect($scope.publish_queue.length).toBe(3);
        $scope.publish_queue[0].selected = true;
        $scope.publish_queue[1].selected = true;
        $scope.selectQueuedItem($scope.publish_queue[0]);
        $scope.selectQueuedItem($scope.publish_queue[1]);
        expect($scope.multiSelectCount).toBe(2);
        expect($scope.showResendBtn).toBe(true);
        expect($scope.showCancelBtn).toBe(false);
        $scope.publish_queue[1].selected = false;
        $scope.selectQueuedItem($scope.publish_queue[1]);
        $scope.cancelSelection();
        expect($scope.multiSelectCount).toBe(0);
    }));

    it('sets the selected filter channel', inject(function() {
        var channelValue = {foo: 'bar'};
        $scope.selectedFilterChannel = null;
        $scope.filterSchedule(channelValue, 'channel');
        expect($scope.selectedFilterChannel).toEqual(channelValue);
    }));

    it('sets the selected filter subscriber', inject(function() {
        var subscriberValue = {foo: 'bar'};
        $scope.selectedFilterSubscriber = null;
        $scope.filterSchedule(subscriberValue, 'subscriber');
        expect($scope.selectedFilterSubscriber).toEqual(subscriberValue);
    }));

    it('can resend single publish queue item', inject(function($rootScope, api, $q) {
        $rootScope.$digest();
        expect($scope.publish_queue.length).toBe(3);
        spyOn(api.publish_queue, 'save').and.callFake(function () {
            publish_queue._items.push($scope.buildNewSchedule($scope.publish_queue[0]));
            return $q.when();
        });
        $scope.scheduleToSend($scope.publish_queue[0]);
        expect($scope.publish_queue.length).toBe(4);
    }));
});
