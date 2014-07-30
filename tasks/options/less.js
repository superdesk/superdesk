
var files = [
    {
        dest: '<%= distDir %>/styles/css/bootstrap.css',
        src: '<%= appDir %>/styles/less/bootstrap.less'
    }, {
        expand: true,
        dest: '<%= tmpDir %>/',
        cwd: '<%= appDir %>/scripts/',
        src: ['superdesk/**/*.less', 'superdesk-*/**/*.less'],
        ext: '.css'
    }
];

module.exports = {
    dev: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: files
    },
    prod: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: files
    }
};
