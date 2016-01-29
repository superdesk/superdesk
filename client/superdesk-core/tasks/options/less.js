
var files = [
    {
        dest: '<%= distDir %>/bootstrap.css',
        src: '<%= coreDir %>/styles/less/bootstrap.less'
    },
    {
        dest: '<%= distDir %>/app.css',
        src: '<%= appDir %>/index.less',
    },
    {
        expand: true,
        dest: '<%= tmpDir %>/docs/',
        cwd: '<%= coreDir %>/docs/',
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
            paths: [
                '<%= coreDir %>/styles/less',
                '<%= coreDir %>/scripts',
                '<%= appDir %>/'
            ],
            compress: false,
            cleancss: true
        },
        files: files
    },
    docs: {
        options: {
            paths: ['<%= coreDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: [files[0], files[2]]
    },
    prod: {
        options: {
            paths: [
                '<%= coreDir %>/styles/less',
                '<%= coreDir %>/scripts',
                '<%= appDir %>/'
            ],
            compress: false,
            cleancss: true
        },
        files: files
    }
};
