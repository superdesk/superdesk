import {startApp} from 'superdesk-core/scripts/index';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';
import markForUserExtension from 'superdesk-core/scripts/extensions/markForUser';

setTimeout(() => {
    startApp(
        [
            planningExtension,
            markForUserExtension,
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
