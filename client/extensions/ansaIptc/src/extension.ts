import {IExtension, IExtensionActivationResult, ISuperdesk, IArticle, ISubject, IUser} from 'superdesk-api';

const PHOTO_CATEGORIES_ID = 'PhotoCategories';

// convert 20191209 to 2019-12-09
const parseDate = (date: string) => date.length === 8 ?
    [
        date.substr(0, 4),
        date.substr(4, 2),
        date.substr(6, 2),
    ].join('-') : date;

// convert 152339+0000 to 15:23:39+0000
const parseTime = (time: string) => time.length >= 6 ?
    [
        time.substr(0, 2),
        time.substr(2, 2),
        time.substr(4),
    ].join(':') : time;

const parseDatetime = (date?: string, time?: string) => (date && time) ?
    `${parseDate(date)}T${parseTime(time)}` :
    null;

const extension: IExtension = {
    id: 'ansa-iptc',
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                iptcMapping: (data, item: IArticle) => Promise.all([
                    superdesk.entities.vocabulary.getIptcSubjects(),
                    superdesk.entities.vocabulary.getVocabulary(PHOTO_CATEGORIES_ID),
                    superdesk.session.getCurrentUser(),
                ]).then(([subjects, categories, user]: [Array<ISubject>, Array<ISubject>, IUser]) => {
                    const subjectReference = Array.isArray(data.SubjectReference) ? data.SubjectReference : [data.SubjectReference || ''];
                    const signOff = user.sign_off || user.username;

                    Object.assign(item, {
                        sign_off: signOff,
                        slugline: data.ObjectName,
                        byline: data['By-line'] || [
                            user.first_name,
                            user.last_name,
                        ].filter((value) => value).join(' '),
                        headline: data.Headline,
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
                            coauthor: data['By-lineTitle'] || signOff,
                            supplier: data.Source,
                        },
                    });

                    if (item.extra) {
                        const created = parseDatetime(data.DateCreated, data.TimeCreated);
                        const release = parseDatetime(data.ReleaseDate, data.ReleaseTime);

                        if (created && created !== '') {
                            item.extra.DateCreated = created;
                        }

                        if (release) {
                            item.extra.DateRelease = release;
                        }
                    }

                    // generate random id using timestamp + random bits
                    // will be used as filename when ingesting same binary again
                    item.uri = Date.now().toString(36) + Math.random().toString(36).substr(2) + '.jpg';

                    console.debug('iptc', data, item);

                    return item;
                }),
            },
        };

        return Promise.resolve(result);
    },
};

export default extension;
