import {startApp} from 'superdesk-core/scripts/index';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';
import markForUserExtension from 'superdesk-core/scripts/extensions/markForUser';
import annotationsLibraryExtension from 'superdesk-core/scripts/extensions/annotationsLibrary/dist/src/extension';
import datetimeFieldExtension from 'superdesk-core/scripts/extensions/datetimeField/dist/src/extension';

setTimeout(() => {
    startApp(
        [
            planningExtension,
            markForUserExtension,
            annotationsLibraryExtension, 
            datetimeFieldExtension
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
