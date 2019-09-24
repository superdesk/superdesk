
import AnsaStagesAutoPublish from './AnsaStagesAutoPublish';

export default angular.module('ansa.widgets', [])
    .controller('AnsaStagesAutoPublish', AnsaStagesAutoPublish)
    .config(['authoringWidgetsProvider', (authoringWidgetsProvider) => {
        authoringWidgetsProvider.widget('ansa-semantics', {
            label: 'Semantics',
            icon: 'semantics',
            template: 'ansa-semantics-widget.html',
            order: 7,
            side: 'right',
            display: {authoring: true, picture: true, personal: true},
            configurable: false,
        });

        authoringWidgetsProvider.widget('related-item', {
            label: 'Related Items',
            icon: 'related',
            template: 'ansa-related-widget.html',
            order: 7,
            side: 'right',
            display: {authoring: true, picture: true, personal: true},
            configurable: false,
        });
    }])
    .config(['dashboardWidgetsProvider', (dashboardWidgets) => {
        dashboardWidgets.addWidget('stages-auto-publish', {
            label: gettext('Auto Publishing'),
            icon: 'switches',
            max_sizex: 1,
            max_sizey: 2,
            sizex: 1,
            sizey: 1,
            template: 'stages-auto-publish.html',
            description: 'Configure auto publishing',
            thumbnail: require('./thumbnail.svg'),
        });
    }])
    .run(['$templateCache', ($templateCache) => {
        $templateCache.put('ansa-semantics-widget.html', require('./ansa-semantics-widget.html'));
        $templateCache.put('ansa-related-widget.html', require('./ansa-related-widget.html'));
        $templateCache.put('stages-auto-publish.html', require('./stages-auto-publish.html'));
    }])
;
