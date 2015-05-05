define(['./analytics'], function(analyticsModule) {
    'use strict';

    describe('analytics', function() {

        beforeEach(module(analyticsModule.name));
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
});
