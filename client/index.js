import {startApp} from 'superdesk-core/scripts/index';
import {SamsAttachmentsWidget} from 'superdesk-core/scripts/extensions/sams/dist/src/apps/samsAttachmentsWidget';

setTimeout(() => {
    startApp(
         [
            {
                id: 'annotationsLibrary',
                load: () => import('superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension').then((res) => res.default),
            },
            {
                id: 'markForUser',
                load: () => import('superdesk-core/scripts/extensions/markForUser/dist/src/extension').then((res) => res.default),
            },
            {
                id: 'datetimeField',
                load: () => import('superdesk-core/scripts/extensions/datetimeField/dist/src/extension').then((res) => res.default),
            },
             {
                 id: 'samsExtension',
                 load: () => import('superdesk-core/scripts/extensions/sams/dist/src/extension').then((res) => res.default),
             }
        ],
        {
            AuthoringAttachmentsWidget: SamsAttachmentsWidget,
        }
    )
});

export default angular.module('main.superdesk', []);
