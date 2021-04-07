import {startApp} from 'superdesk-core/scripts/index';
import annotationsLibraryExtension from 'superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension';
import markForUserExtension from 'superdesk-core/scripts/extensions/markForUser/dist/src/extension';
import datetimeFieldExtension from 'superdesk-core/scripts/extensions/datetimeField/dist/src/extension';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';

setTimeout(() => {
    startApp(
        [
            annotationsLibraryExtension,
            markForUserExtension,
            datetimeFieldExtension,
            planningExtension,
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
