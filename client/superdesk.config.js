module.exports = function(grunt) {
    return {
        defaultRoute: '/workspace/personal',
        requiredMediaMetadata: ['headline', 'description_text', 'alt_text'],
        features: {noTakes: 1},
        publisher: {
            protocol: 'https',
            tenant: 'default',
            domain: process.env.PUBLISHER_API_DOMAIN || '',
            base: 'api/v1'
        }
    };
};
