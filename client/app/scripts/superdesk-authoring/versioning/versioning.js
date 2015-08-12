(function() {

'use strict';

angular.module('superdesk.authoring.versioning', [])
    .config(['authoringWidgetsProvider', function(authoringWidgetsProvider) {
        authoringWidgetsProvider
            .widget('versioning', {
                icon: 'revision',
                label: gettext('Versioning'),
                removeHeader: true,
                template: 'scripts/superdesk-authoring/versioning/views/versioning.html',
                order: 4,
                side: 'right',
                display: {authoring: true, packages: true, legalArchive: true}
            });
    }]);

})();
