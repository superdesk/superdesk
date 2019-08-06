import {ISuperdesk, IExtension, IExtensionActivationResult} from 'superdesk-api';
import {getWidgets} from './get-widgets';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                articleListItemWidgets: [getWidgets(superdesk)],
                articleGridItemWidgets: [getWidgets(superdesk)],
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
