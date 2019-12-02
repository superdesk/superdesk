import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, ISubject} from 'superdesk-api';

const PHOTO_CATEGORIES_ID = 'PhotoCategories';

// convert 20191209 to 2019-12-09
const parseDate = (date: string) => date.length === 8 ?
    [
        date.substr(0, 4),
        date.substr(4, 2),
        date.substr(6, 2),
    ].join('-') : date;

// convert 152339+0000 to 15:23:39+0000
const parseTime = (time: string) => time.length === 11 ?
    [
        time.substr(0, 2),
        time.substr(2, 4),
        time.substr(4),
    ].join(':') : time;

const parseDatetime = (date: string, time: string) => (date && time) ?
    `${parseDate(date)}T${parseTime(time)}` :
    null;

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item: IArticle) => Promise.all([
                    superdesk.entities.vocabulary.getIptcSubjects(),
                    superdesk.entities.vocabulary.getVocabulary(PHOTO_CATEGORIES_ID),
                ]).then(([subjects, categories]: [Array<ISubject>, Array<ISubject>]) => {
                    const subjectReference = Array.isArray(data.SubjectReference) ? data.SubjectReference : [data.SubjectReference || ''];

                    Object.assign(item, {
                        slugline: data.ObjectName,
                        byline: data['By-line'],
                        sign_off: data['By-lineTitle'] || item.sign_off,
                        headline: data.Headline,
                        source: data.Source,
                        copyrightholder: data.Credit,
                        copyrightnotice: data.CopyrightNotice,
                        usageterms: data.CopyrightNotice,
                        language: data.LanguageIdentifier || 'it',
                        subject: (item.subject || []).concat(
                            subjects.filter((subj) => subjectReference.find((ref) => ref.includes(subj.qcode))),
                            data.Category != null ?
                                categories.filter((cat) => cat.name === data.Category)
                                    .map((cat) => ({name: cat.name, qcode: cat.qcode, scheme: PHOTO_CATEGORIES_ID})) :
                                [],
                        ),
                        extra: {
                            city: data.City,
                            nation: data['Country-PrimaryLocationName'],
                            digitator: data['Writer-Editor'],
                            DateCreated: parseDatetime(data.DateCreated, data.TimeCreated),
                            DateRelease: parseDatetime(data.ReleaseDate, data.ReleaseTime),
                        },
                    });

                    return item;
                }),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
