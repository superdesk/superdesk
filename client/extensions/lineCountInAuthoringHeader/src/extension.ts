import {ISuperdesk, IExtension, IExtensionActivationResult} from 'superdesk-api';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            
        };

        return Promise.resolve(result);
    },
};

export default extension;
