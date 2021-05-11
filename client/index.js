import {startApp} from 'superdesk-core/scripts/index';
import {SamsAttachmentsWidget} from 'superdesk-core/scripts/extensions/sams/dist/src/apps/samsAttachmentsWidget';

setTimeout(() => {
    startApp(
        [
            {
                id: 'annotationsLibrary',
                load: () => import('superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension'),
            },
            {
                id: 'markForUser',
                load: () => import('superdesk-core/scripts/extensions/markForUser/dist/src/extension'),
            },
            {
                id: 'datetimeField',
                load: () => import('superdesk-core/scripts/extensions/datetimeField/dist/src/extension'),
            },
            {
                id: 'sams',
                load: () => import('superdesk-core/scripts/extensions/sams/dist/src/extension'),
            },
        ],
        {
            AuthoringAttachmentsWidget: SamsAttachmentsWidget,
        },
    );
});

export default angular.module('main.superdesk', []);
