import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [{
            id: 'planning',
            load: () => (
                import('superdesk-planning/client/planning-extension/dist/extension')
                    .then((res) => res.default)
            ),
        }],
        {}
    )
});

export default angular.module('main.superdesk', []);
