
module.exports = {
    options: {
        encofing: 'utf8',
        algorithm: 'md5',
        length: 8
    },
    css: {
        src: '<%= distDir %>/*.css',
        dest: '<%= distDir %>/'
    },
    js: {
        src: '<%= distDir %>/*.js',
        dest: '<%= distDir %>/'
    }
};
