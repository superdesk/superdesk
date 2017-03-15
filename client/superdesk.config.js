module.exports = function(grunt) {
    return {
        defaultRoute: '/workspace/personal',
        requiredMediaMetadata: ['headline', 'description_text', 'alt_text'],
        features: {noTakes: 1},
        publisher: {
            protocol: 'https',
            tenant: process.env.PUBLISHER_API_SUBDOMAIN || '',
            domain: process.env.PUBLISHER_API_DOMAIN || 'localhost',
            base: 'api/v1'
        }
    };
};
