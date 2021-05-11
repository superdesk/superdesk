import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [{
            id: 'planning',
            load: () => import('superdesk-planning/client/planning-extension/dist/extension'),
        }],
        {}
    )
});

export default angular.module('main.superdesk', []);
