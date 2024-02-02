import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
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
                id: 'planning-extension',
                load: () => import('superdesk-planning/client/planning-extension'),
            },
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
