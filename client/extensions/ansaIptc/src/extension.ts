import {IExtension, IExtensionActivationResult, ISuperdesk} from 'superdesk-api';

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item) => Promise.all([
                    superdesk.entities.vocabulary.getIptcSubjects(),
                ]).then(([subjects]) =>
                    Object.assign(item, {
                        subject: data.SubjectReference != null ?
                            subjects.filter((subj) => subj.qcode === data.SubjectReference) :
                            [],
                        extra: {
                            city: data.City,
                            nation: data['Country-PrimaryLocationName'],
                        },
                    }),
                ),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
