(function() {
    'use strict';

    describe('analytics', function() {

        beforeEach(module('superdesk.analytics'));
        beforeEach(module(function($provide) {
            $provide.constant('config', {
                analytics: {piwik: {}, ga: {}}
            });
        }));

        it('can track activity', inject(function(analytics, $rootScope) {
            spyOn(analytics, 'track');

            var activity = {
                _id: 'test',
                label: 'test'
            };

            // mimic route change event
            $rootScope.$broadcast('$routeChangeSuccess', activity);

            expect(analytics.track).toHaveBeenCalledWith(activity);
        }));
    });
})();
