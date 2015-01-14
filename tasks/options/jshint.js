
module.exports = {
    options: {
        jshintrc: '.jshintrc'
    },
    all: require('./files').scripts,
    docs: ['<%= appDir %>/docs/**/*.js']
};
