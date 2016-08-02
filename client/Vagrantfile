# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.define "superdesk-client" do |app|
        app.vm.provider "docker" do |d|
            d.build_dir = "."
            d.cmd = ['grunt', 'server', '--server=http://localhost:5000', '--force']
            d.ports = ["9000:9000",]
            d.name = "superdesk-client"
            d.build_args = ["--tag='superdesk/client'"]
        end
    end
end
