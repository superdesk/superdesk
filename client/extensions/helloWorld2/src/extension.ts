import {ISuperdesk, IExtension} from 'superdesk-api';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const {gettext} = superdesk.localization;

        superdesk.ui.alert(gettext('Hello world'));

        return Promise.resolve({});
    },
};

export default extension;
