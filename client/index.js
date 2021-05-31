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
                id: 'markForUserExtension',
                load: () => import('superdesk-core/scripts/extensions/markForUser'),
            },
            {
                id: 'datetimeFieldExtension',
                load: () => import('superdesk-core/scripts/extensions/datetimeField'),
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
