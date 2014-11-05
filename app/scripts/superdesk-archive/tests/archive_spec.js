'use strict';

describe('content', function() {
    beforeEach(module('superdesk.archive'));
    beforeEach(module('superdesk.mocks'));

    it('can spike items', inject(function(spike, api, $q) {
        spyOn(api, 'save').andReturn($q.when());
        spike.spike({});
        expect(api.save).toHaveBeenCalled();
    }));

    it('can unspike items', inject(function(spike, api, $q) {
        spyOn(api, 'remove').andReturn($q.when());
        spike.unspike({});
        expect(api.remove).toHaveBeenCalled();
    }));
});
