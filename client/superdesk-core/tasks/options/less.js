
var files = [
    {
        dest: '<%= distDir %>/styles/css/bootstrap.css',
        src: '<%= appDir %>/styles/less/bootstrap.less'
    },
    {
        expand: true,
        dest: '<%= tmpDir %>/',
        cwd: '<%= appDir %>/scripts/',
        src: ['superdesk*/**/*.less'],
        ext: '.css'
    }, {
        expand: true,
        dest: '<%= tmpDir %>/docs/',
        cwd: '<%= appDir %>/docs/',
        src: ['styles/*.less'],
        ext: '.css'
    }
];

module.exports = {
    bower: {
        files: [
            {
                dest: '<%= bowerDir %>/styles/css/bootstrap.css',
                src: '<%= appDir %>/styles/less/bootstrap.less'
            }, {
                expand: true,
                dest: '<%= tmpDir %>/',
                cwd: '<%= appDir %>/scripts/',
                src: ['superdesk/**/*.less', 'superdesk-*/**/*.less'],
                ext: '.css'
            }
        ],
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        }
    },
    dev: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: files
    },
    docs: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: [files[0], files[2]]
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
