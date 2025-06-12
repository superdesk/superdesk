import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
            {
                id: 'annotationsLibrary',
                load: () => import('superdesk-core/scripts/extensions/annotationsLibrary'),
            },
            {
                id: 'markForUser',
                load: () => import('superdesk-core/scripts/extensions/markForUser'),
            },
            {
                id: 'datetimeField',
                load: () => import('superdesk-core/scripts/extensions/datetimeField'),
            },
            {
                id: 'broadcasting',
                load: () => import('superdesk-core/scripts/extensions/broadcasting').then((broadcasting) => {
                    broadcasting.setCustomizations({
                        getRundownItemDisplayName: (rundown) => rundown.technical_title,
                    });

                    return broadcasting;
                }),
            },
            {
                id: 'availability-manager',
                load: () => import('superdesk-core/scripts/extensions/availability-manager').then((extension) => {
                    extension.configure({
                        dashboard: {
                            addLinkToSideMenu: {
                                icon: 'user',
                                order: 1100,
                                keyBinding: 'ctrl+alt+c',
                            },

                            tags: {
                                leafsOnly: true,
                            },
                        },
                    });

                    return extension;
                }),
            },
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
