
module.exports = {
    options: {
        encofing: 'utf8',
        algorithm: 'md5',
        length: 8
    },
    css: {
        src: '<%= serverDir %>/styles/css/*.css',
        dest: '<%= serverDir %>/styles/css/'
    },
    js: {
        src: '<%= serverDir %>/scripts/*.js',
        dest: '<%= serverDir %>/scripts/'
    }
};
