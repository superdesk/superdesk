
var openUrl = require('./helpers/utils').open;
var workspace = require('./helpers/pages').workspace;
var content = require('./helpers/pages').content;
var editArticle = require('./helpers/pages').editArticle;

describe('HIGHLIGHTS', function() {
    'use strict';

    var Highlights = function() {
      this.list = element.all(by.repeater('config in configurations._items'));
      this.name = element(by.model('configEdit.name'));
      this.desks = element.all(by.repeater('desk in assignedDesks'));
      this.highlights = element.all(by.repeater('h in highlights'));

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

	  this.getHighlights = function() {
		  return this.highlights.filter(function(elem, index) {
			  return elem.getText().then(function(text) {
				  return text;
			  });
		  });
	  };

	  this.selectHighlight = function(name) {
		  this.highlights.all(by.css('[option="' + name.toUpperCase() + '"]')).click();
	  };
    };

    describe('add highlights configuration:', function() {
    	beforeEach(openUrl('/#/settings/highlights'));

		it('add highlights configuration with one desk', function() {
	    	var highlights = new Highlights();
			highlights.add();
			highlights.setName('highlight new');
			highlights.toggleDesk('Sports Desk');
			highlights.save();
			expect(highlights.getRow('highlight new').count()).toBe(1);
	        highlights.edit('highlight new');
		    highlights.expectDeskSelection('Sports Desk', true);
		});

        it('add highlights configuration with the same name', function() {
	    	var highlights = new Highlights();
			highlights.add();
			highlights.setName('Highlight one');
			highlights.save();
			highlights.cancel();
			expect(highlights.getRow('Highlight one').count()).toBe(1);
        });

        it('add highlights configuration with no desk', function() {
	    	var highlights = new Highlights();
			highlights.add();
			highlights.setName('highlight new');
			highlights.save();
			expect(highlights.getRow('highlight new').count()).toBe(1);
        });
    });

    describe('edit highlights configuration:', function() {
        beforeEach(openUrl('/#/settings/highlights'));

        it('change the name of highlight configuration', function() {
	    	var highlights = new Highlights();
			highlights.edit('highlight one');
			highlights.setName('highlight new');
			highlights.save();
			expect(highlights.getRow('highlight new').count()).toBe(1);
			expect(highlights.getRow('highlight one').count()).toBe(0);
        });

        it('add a desk to highlight configuration', function() {
	    	var highlights = new Highlights();
			highlights.edit('highlight one');
			highlights.toggleDesk('Politic Desk');
			highlights.save();
			highlights.edit('highlight one');
			highlights.expectDeskSelection('Politic Desk', true);
        });

        it('delete a desk from highlight configuration', function() {
	    	var highlights = new Highlights();
			highlights.edit('highlight one');
			highlights.toggleDesk('Sports Desk');
			highlights.save();
			highlights.edit('highlight one');
			highlights.expectDeskSelection('Sports Desk', false);
        });
    });

  describe('delete highlights configuration:', function() {
	  beforeEach(openUrl('/#/settings/highlights'));

	  it('delete highlight configuration', function() {
	  		var highlights = new Highlights();
			expect(highlights.getRow('highlight one').count()).toBe(1);
			highlights.remove('highlight one');
			expect(highlights.getRow('highlight one').count()).toBe(0);
	  });
  });

describe('mark for highlights in a desk:', function() {
	var highlights = new Highlights();
    beforeEach(openUrl('/#/workspace/content'));

    it('mark for highlights in list view', function() {
    	workspace.switchToDesk('SPORTS DESK');
    	content.setListView();
    	content.actionOnItem('Mark item', 0);
    	expect(highlights.getHighlights().count()).toBe(2);
    	highlights.selectHighlight('Highlight one');
    	workspace.switchToDesk('PERSONAL');
    	workspace.switchToDesk('SPORTS DESK');
    	content.setListView();
    	content.checkMarkedForHighlight('Highlight one', 0);
    });

    it('mark for highlights in edit article screen', function() {
    	workspace.switchToDesk('SPORTS DESK');
    	content.setListView();
    	content.actionOnItem('Edit item', 0);
    	editArticle.markAction();
    	expect(highlights.getHighlights().count()).toBe(2);
    	highlights.selectHighlight('Highlight one');
    	editArticle.closeAction();
    	workspace.switchToDesk('PERSONAL');
    	workspace.switchToDesk('SPORTS DESK');
    	content.setListView();
    	content.checkMarkedForHighlight('Highlight one', 0);
    });
});
});
