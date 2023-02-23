import {startApp} from 'superdesk-core/scripts/index';

setTimeout(() => {
    startApp(
        [
            {
                id: 'broadcasting',
                load: () => import('superdesk-core/scripts/extensions/broadcasting').then((broadcasting) => {
                    broadcasting.setCustomizations({
                        getRundownItemDisplayName: (rundown) => rundown.technical_title,
                    });

                    return broadcasting;
                }),
            },
        ],
        {},
    );
});

export default angular.module('main.superdesk', []);
