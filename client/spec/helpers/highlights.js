
'use strict';

var openUrl = require('./helpers/utils').open;

module.exports = new Highlights();

function Highlights() {
	this.list = element.all(by.repeater('config in configurations._items'));
	this.name = element(by.model('configEdit.name'));
	this.desks = element.all(by.repeater('desk in assignedDesks'));
	
	this.get = function() {
	  openUrl('/#/settings/highlights');
	};

	  this.getRow = function(name) {
		  return this.list.filter(function(elem, index) {
			  return elem.element(by.binding('config.name')).getText().then(function(text) {
			    return text.toUpperCase() === name.toUpperCase();
			  });
		  });
	  };
	
	  this.getCount = function(index) {
		return this.list.count();
	  };
	
	  this.add = function() {
		element(by.className('icon-plus-sign')).click();
	    browser.sleep(500);
	  };
	
	  this.edit = function(name) {
		this.getRow(name).then(function(rows) {
			rows[0].click();
			rows[0].element(by.className('icon-pencil')).click();
	    	browser.sleep(500);
		});
	  };
	
	  this.remove = function(name) {
		this.getRow(name).then(function(rows) {
			rows[0].click();
			rows[0].element(by.className('icon-trash')).click();
		browser.sleep(500);
		element(by.buttonText('OK')).click();
		});
	  };
	
	  this.getName = function() {
	    return this.name.getText();
	  };
	
	  this.setName = function(name) {
		  this.name.clear();
		  this.name.sendKeys(name);
	  };
	
	  this.getDesk = function(name) {
		  return this.desks.filter(function(elem, index) {
			  return elem.element(by.binding('desk.name')).getText().then(function(text) {
			    return text.toUpperCase() === name.toUpperCase();
			  });
		  });
	  };
	
	  this.toggleDesk = function(name) {
		  this.getDesk(name).then(function(desks) {
			  desks[0].element(by.className('sd-checkbox')).click();
		  });
	  };
	
	  this.expectDeskSelection = function(name, selected) {
		  this.getDesk(name).then(function(desks) {
			  if (selected) {
				  expect(desks[0].element(by.className('sd-checkbox')).getAttribute('checked')).toBe('true');
		  } else {
			  expect(desks[0].element(by.className('sd-checkbox')).getAttribute('checked')).toBe(null);
			  }
		  });
	  };
	
	  this.save = function() {
		  element(by.css('[ng-click="save()"]')).click();
	  };
	
	  this.cancel = function() {
		  element(by.css('[ng-click="cancel()"]')).click();
	  };
	
	  this.getHighlights = function(elem) {
		  return elem.all(by.repeater('h in highlights')).filter(function(elem, index) {
			  return elem.getText().then(function(text) {
				  return text;
			  });
		  });
	  };
	
	  this.selectHighlight = function(elem, name) {
		  elem.all(by.repeater('h in highlights')).all(by.css('[option="' + name.toUpperCase() + '"]')).click();
	  };
	
	  this.createHighlightsPackage = function(highlight) {
		  element(by.className('svg-icon-create-list')).click();
	  this.selectHighlight(element(by.id('highlightPackage')), highlight);
	  };
	
	  this.switchHighlightFilter = function(name) {
		  element(by.id('search-highlights')).element(by.className('icon-dots-vertical')).click();
	  element(by.id('search-highlights')).element(by.css('[option="' + name.toUpperCase() + '"]')).click();
	  };
	
	  this.exportHighlights = function() {
		  element(by.id('export')).click();
	  };
}
