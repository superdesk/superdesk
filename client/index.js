import {startApp} from 'superdesk-core/scripts/index';
import planningExtension from 'superdesk-planning/client/planning-extension/dist/extension';

setTimeout(() => {
    startApp(
        [planningExtension],
        {},
    );
});

export default angular.module('main.superdesk', []);
