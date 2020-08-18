import {startApp} from 'superdesk-core/scripts/index';
import annotationsLibraryExtension from 'superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension';
import markForUserExtension from 'superdesk-core/scripts/extensions/markForUser/dist/src/extension';
import datetimeFieldExtension from 'superdesk-core/scripts/extensions/datetimeField/dist/src/extension';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';
import samsExtension from 'superdesk-core/scripts/extensions/sams/dist/src/extension';

setTimeout(() => {
    startApp(
        [
            annotationsLibraryExtension,
            markForUserExtension,
            datetimeFieldExtension,
            planningExtension,
            samsExtension,
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
