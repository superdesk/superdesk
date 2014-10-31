
module.exports = {
    options: {
        encofing: 'utf8',
        algorithm: 'md5',
        length: 8
    },
    css: {
        src: '<%= distDir %>/styles/css/*.css',
        dest: '<%= distDir %>/styles/css/'
    },
    js: {
        src: '<%= distDir %>/scripts/*.js',
        dest: '<%= distDir %>/scripts/'
    }
};
