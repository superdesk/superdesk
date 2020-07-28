import {ISuperdesk, IExtension, IExtensionActivationResult} from 'superdesk-api';
import {getLineCountToolbarWidget} from './line-count-toolbar-widget';

const extension: IExtension = {
    id: 'lineCountInAuthoringHeader',
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                authoringTopbar2Widgets: [getLineCountToolbarWidget(superdesk)],
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
