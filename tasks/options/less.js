module.exports = {
    dev: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: false,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less',
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/users.less',
            '<%= distDir %>/styles/css/dashboard.css': '<%= appDir %>/scripts/superdesk-dashboard/styles/dashboard.less',
            '<%= distDir %>/styles/css/widget-ingest.css': '<%= appDir %>/scripts/superdesk-ingest/ingest-widget/widget-ingest.less',
            '<%= distDir %>/styles/css/widget-world-clock.css': '<%= appDir %>/scripts/superdesk-dashboard/widgets/worldClock/world-clock.less',
            '<%= distDir %>/styles/css/settings.css': '<%= appDir %>/scripts/superdesk-settings/styles/settings.less',
            '<%= distDir %>/styles/css/uploader.css': '<%= appDir %>/scripts/superdesk/upload/styles/uploader.less',
            '<%= distDir %>/styles/css/media-archive.css': '<%= appDir %>/scripts/superdesk-items-common/styles/media-archive.less',
            '<%= distDir %>/styles/css/desks.css': '<%= appDir %>/scripts/superdesk-desks/styles/desks.less',
            '<%= distDir %>/styles/css/menu.css': '<%= appDir %>/scripts/superdesk/menu/styles/menu.less',
            '<%= distDir %>/styles/css/notify.css': '<%= appDir %>/scripts/superdesk/notify/styles/notify.less',
            '<%= distDir %>/styles/css/login.css': '<%= appDir %>/scripts/superdesk/auth/login-modal.less'
        }
    },
    prod: {
        options: {
            paths: ['<%= appDir %>/styles/less'],
            compress: true,
            cleancss: true
        },
        files: {
            '<%= distDir %>/styles/css/bootstrap.css': '<%= appDir %>/styles/less/bootstrap.less',
            '<%= distDir %>/styles/css/users.css': '<%= appDir %>/scripts/superdesk-users/styles/users.less',
            '<%= distDir %>/styles/css/dashboard.css': '<%= appDir %>/scripts/superdesk-dashboard/styles/dashboard.less',
            '<%= distDir %>/styles/css/widget-ingest.css': '<%= appDir %>/scripts/superdesk-ingest/ingest-widget/widget-ingest.less',
            '<%= distDir %>/styles/css/widget-world-clock.css': '<%= appDir %>/scripts/superdesk-dashboard/widgets/worldClock/world-clock.less',
            '<%= distDir %>/styles/css/settings.css': '<%= appDir %>/scripts/superdesk-settings/styles/settings.less',
            '<%= distDir %>/styles/css/uploader.css': '<%= appDir %>/scripts/superdesk/upload/styles/uploader.less',
            '<%= distDir %>/styles/css/media-archive.css': '<%= appDir %>/scripts/superdesk-items-common/styles/media-archive.less',
            '<%= distDir %>/styles/css/desks.css': '<%= appDir %>/scripts/superdesk-desks/styles/desks.less',
            '<%= distDir %>/styles/css/menu.css': '<%= appDir %>/scripts/superdesk/menu/styles/menu.less',
            '<%= distDir %>/styles/css/notify.css': '<%= appDir %>/scripts/superdesk/notify/styles/notify.less',
            '<%= distDir %>/styles/css/login.css': '<%= appDir %>/scripts/superdesk/auth/login-modal.less'
        }
    }
};
