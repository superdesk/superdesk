import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
            {
                id: 'annotationsLibrary',
                load: () => import('superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension'),
            },
            {
                id: 'markForUserExtension',
                load: () => import('superdesk-core/scripts/extensions/markForUser/dist/src/extension'),
            },
            {
                id: 'datetimeFieldExtension',
                load: () => import('superdesk-core/scripts/extensions/datetimeField/dist/src/extension'),
            },
            {
                id: 'planning-extension',
                load: () => import('@superdesk/planning-extension/dist/planning-extension/src/extension'),
            },
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
