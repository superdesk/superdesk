import {startApp} from 'superdesk-core/scripts/index';
import {SamsAttachmentsWidget} from 'superdesk-core/scripts/extensions/sams/dist/src/apps/samsAttachmentsWidget';

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
                id: 'planning-extension',
                load: () => import('superdesk-planning/client/planning-extension'),
            },
            {
                id: 'sams',
                load: () => import('superdesk-core/scripts/extensions/sams'),
            },
        ],
        {
            AuthoringAttachmentsWidget: SamsAttachmentsWidget,
        },
    );
});

export default angular.module('main.superdesk', []);
