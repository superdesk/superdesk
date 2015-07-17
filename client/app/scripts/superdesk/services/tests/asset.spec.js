
'use strict';

describe('superdesk.asset module', function() {

    beforeEach(module('superdesk.asset'));
    beforeEach(module(function($provide) {
        $provide.constant('config', {paths: {superdesk: 'scripts/bower_components/superdesk/app/'}});
    }));

    var asset;
    beforeEach(inject(function($injector) {
        asset = $injector.get('asset');
    }));

    it('can get templateUrl with scripts prefix', function() {
        var templateUrl = asset.templateUrl('superdesk-users/views/user-list-item.html');
        expect(templateUrl)
        .toBe('scripts/bower_components/superdesk/app/scripts/superdesk-users/views/user-list-item.html');
    });

    it('can get templateUrl for relative path', function() {
        var templateUrl = asset.templateUrl('/scripts/superdesk-users/views/user-list-item.html');
        expect(templateUrl)
        .toBe('scripts/bower_components/superdesk/app/scripts/superdesk-users/views/user-list-item.html');
    });

    it('can get templateUrl for absolute path', function() {
        var templateUrl = asset.templateUrl('http://localhost/scripts/superdesk-users/user-list-item.html');
        expect(templateUrl)
        .toBe('http://localhost/scripts/superdesk-users/user-list-item.html');
    });

    it('can get imageUrl', function() {
        var imageUrl = asset.imageUrl('superdesk-users/activity/thumbnail.png');
        expect(imageUrl)
        .toBe('scripts/bower_components/superdesk/app/scripts/superdesk-users/activity/thumbnail.png');
    });

    it('can get imageUrl for relative path', function() {
        var imageUrl = asset.imageUrl('../scripts/superdesk-users/activity/thumbnail.png');
        expect(imageUrl)
        .toBe('scripts/bower_components/superdesk/scripts/superdesk-users/activity/thumbnail.png');
    });

});
