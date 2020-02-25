import {ISuperdesk, IExtension} from 'superdesk-api';

const extension: IExtension = {
    id: 'helloWorld',
    activate: (superdesk: ISuperdesk) => {
        const {gettext} = superdesk.localization;

        superdesk.ui.alert(gettext('Hello world'));

        return Promise.resolve({});
    },
};

export default extension;
