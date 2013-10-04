define([
    'angular',
    'angular-resource'
], function(angular) {
    'use strict';

    var ResourceBase = function() {
        this.links = {};
    };
    ResourceBase.prototype.setLinks = function(links) {
        for (var i in links) {
            this.links[i] = links[i].href;
        }
    };

    var ResourceList = function(response) {
        ResourceBase.call(this);

        this.items = [];

        if (response !== undefined) {
            this.items = response._items;

            for (var i = 0; i < response._items.length; i++) {
                this.items[i] = new ResourceItem(response._items[i]);
            }

            this.setLinks(response._links);
        }
    };
    ResourceList.prototype = new ResourceBase();
    ResourceList.prototype.constructor = ResourceList;

    var ResourceItem = function(response) {
        ResourceBase.call(this);

        if (response !== undefined) {
            for (var i in response) {
                if (i !== '_links') {
                    this[i] = response[i];
                }
            }
            
            this.setLinks(response._links);
        }
    };
    ResourceItem.prototype = new ResourceBase();
    ResourceItem.prototype.constructor = ResourceItem;

    //

    angular.module('superdesk.server', ['ngResource']).
        service('server', function($q, $resource) {
            
            return new function() {
                this._createResource = function(resourceName) {
                    var url = ServerConfig.url + '/' + resourceName + '/';
                    var parameters = {};
                    var actions = {
                        'query': {method: 'GET', isArray: false}
                    };
                    
                    return $resource(url, parameters, actions);
                };

                this.readList = function(resourceName, parameters) {
                    var delay = $q.defer();
                    var resource = this._createResource(resourceName);
                    var list = resource.query(parameters,
                        function(response) {
                            var resourceList = new ResourceList(response);
                            delay.resolve(resourceList);
                        },
                        function(response) {
                            delay.reject(response);
                        }
                    );
                    return delay.promise;
                };

                this.readItem = function(resource, id) {

                };
            };
        });
});