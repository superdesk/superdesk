(function() {

'use strict';

angular.module('superdesk.aggregate.widgets', ['superdesk.aggregate', 'superdesk.dashboard.widgets'])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('aggregate', {
                label: 'Monitoring',
                multiple: true,
                icon: 'archive',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: 'scripts/superdesk-monitoring/aggregate-widget/thumbnail.svg',
                template: 'scripts/superdesk-monitoring/aggregate-widget/aggregate-widget.html',
                configurationTemplate: 'scripts/superdesk-monitoring/aggregate-widget/configuration.html',
                description: 'This widget allows you to create literally any content view you may need in Superdesk,' +
                        ' be it production or ingest. All you need is to select a desk, its stages or a saved search.' +
                        ' Name your view once you are done. Enjoy!',
                custom: true
            });
        }]);
})();
