
export default angular.module('ansa.widgets', [])
    .config(['authoringWidgetsProvider', (authoringWidgetsProvider) => {
        authoringWidgetsProvider.widget('ansa-semantics', {
            label: 'Semantics',
            icon: 'view',
            template: 'ansa-semantics-widget.html',
            order: 7,
            side: 'right',
            display: {authoring: true, picture: true},
            configurable: false
        });

        authoringWidgetsProvider.widget('ansa-semantics', {
            label: 'Related Items',
            icon: 'global-search',
            template: 'ansa-related-widget.html',
            order: 7,
            side: 'right',
            display: {authoring: true, picture: true},
            configurable: false
        });
    }])
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put('ansa-semantics-widget.html', require('./ansa-semantics-widget.html'));
        $templateCache.put('ansa-related-widget.html', require('./ansa-related-widget.html'));
    }])
;
