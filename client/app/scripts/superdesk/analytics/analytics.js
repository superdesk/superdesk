(function() {
    'use strict';

    function NoopTracking() {
        this.track = angular.noop;
    }

    function PiwikTracking(config) {
        /* global _paq */
        window._paq = window._paq || [];

        (function(){
            _paq.push(['setSiteId', config.id]);
            _paq.push(['setTrackerUrl', config.url+'/piwik.php']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.type='text/javascript';
            g.defer=true;
            g.async=true;
            g.src=config.url+'/piwik.js';
            s.parentNode.insertBefore(g,s);
        })();

        this.track = function(activity) {
            _paq.push(['trackPageView', activity.label]);
        };
    }

    function GoogleTracking(config) {
        /* global ga */
        (function(i,s,o,g,r,a,m){
            i.GoogleAnalyticsObject=r;
            i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments);};
            i[r].l=1*new Date();a=s.createElement(o);
            m=s.getElementsByTagName(o)[0];
            a.async=1;
            a.src=g;
            m.parentNode.insertBefore(a,m);
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ga('create', config.id, 'sourcefabric.org');

        this.track = function(activity) {
            ga('send', 'pageview', {
                page: activity._id,
                title: activity.label
            });
        };
    }

    angular.module('superdesk.analytics', [])

    .service('analytics', ['config', function(config) {
        if (config.analytics.piwik.url) {
            PiwikTracking.call(this, config.analytics.piwik);
        } else if (config.analytics.ga.id) {
            GoogleTracking.call(this, config.analytics.ga);
        } else {
            NoopTracking.call(this);
        }
    }])

    .run(['$rootScope', 'analytics', function($rootScope, analytics) {
        $rootScope.$on('$routeChangeSuccess', function(ev, route) {
            if (angular.isDefined(route)) {
                analytics.track(route);
            }
        });
    }]);
})();
