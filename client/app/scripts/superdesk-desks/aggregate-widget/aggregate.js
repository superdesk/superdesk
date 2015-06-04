(function() {

'use strict';

angular.module('superdesk.aggregate.widgets', ['superdesk.aggregate.sidebar', 'superdesk.dashboard.widgets'])
        .config(['widgetsProvider', function(widgets) {
            widgets.widget('aggregate', {
                label: 'Aggregate',
                multiple: true,
                icon: 'archive',
                max_sizex: 2,
                max_sizey: 2,
                sizex: 1,
                sizey: 2,
                thumbnail: 'scripts/superdesk-desks/aggregate-widget/thumbnail.png',
                template: 'scripts/superdesk-desks/aggregate-widget/aggregate-widget.html',
                configurationTemplate: 'scripts/superdesk-desks/aggregate-widget/configuration.html',
                description: 'Displaying the aggregate content view.',
                custom: true
            });
        }]);
})();
