module.exports = function(grunt) {
    return {
        defaultRoute: '/workspace/personal',
        features: {noTakes: 1},
        publisher: {
            protocol: 'https',
            tenant: process.env.PUBLISHER_API_SUBDOMAIN || '',
            domain: process.env.PUBLISHER_API_DOMAIN || 'localhost',
            base: 'api/v1'
        },
        validatorMediaMetadata: {
            headline: {required: true},
            alt_text: {required: true},
            description_text: {required: true},
            copyrightholder: {required: false},
            byline: {required: false},
            usageterms: {required: false},
            copyrightnotice: {required: false}
        }
    };
};
