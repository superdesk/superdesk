# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.define "mongo" do |app|
        app.vm.provider "docker" do |d|
            d.image = "dockerfile/mongodb"
            d.name = "mongodb"
        end
    end

    config.vm.define "elastic" do |app|
        app.vm.provider "docker" do |d|
            d.image = "dockerfile/elasticsearch"
            d.name = "elastic"
        end
    end

    config.vm.define "redis" do |app|
        app.vm.provider "docker" do |d|
            d.image = "dockerfile/redis"
            d.name = "redis"
        end
    end

    config.vm.define "superdesk" do |app|
        app.vm.provider "docker" do |d|
            d.build_dir = "."
            d.cmd = ["start"]
            d.ports = ["5000:5000", "5100:5100"]
            d.link "mongodb:mongodb"
            d.link "elastic:elastic"
            d.link "redis:redis"
            d.name = "superdesk"
            d.build_args = ["--tag='superdesk/server'"]
        end
    end
end
