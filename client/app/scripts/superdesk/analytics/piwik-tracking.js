define([], function() {
    'use strict';

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

    return PiwikTracking;
});
