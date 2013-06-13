#/***************************************************************************
# ProfileTool
# 
# ProfileTool
#                             -------------------
#        begin                : 2012-03-03
#        copyright            : (C) 2012 by patricev
#        email                : XXX
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/
# Makefile for a PyQGIS plugin 
PLUGINNAME = profiletool
PY_FILES =  __init__.py  profileplugin.py
PY_FILES1 = doProfile.py  selectPointTool.py
EXTRAS = metadata.txt resources.qrc
UI_FILES1 =  ui/profiletool.py
RESOURCE_FILES = resources.py
TOOL_DIR = tools ui
ICONS_DIR = icons

UI_SOURCES=$(wildcard ui/*.ui)
UI_FILES=$(patsubst %.ui,%.py,$(UI_SOURCES))
RC_SOURCES=$(wildcard *.qrc)
RC_FILES=$(patsubst %.qrc,%.py,$(RC_SOURCES))

GEN_FILES = ${UI_FILES} ${RC_FILES}

all: $(GEN_FILES)
ui: $(UI_FILES)
resources: $(RC_FILES)

$(UI_FILES): %.py: %.ui
	pyuic4 -o $@ $<

$(RC_FILES): %.py: %.qrc
	pyrcc4 -o $@ $<


clean:
	rm -f $(GEN_FILES) *.pyc


compile: $(UI_FILES) $(RESOURCE_FILES)

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis2/python/plugins
deploy: all
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/tools
	mkdir -p $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/icons
	cp -vf $(PY_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(UI_FILES1) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)/tools
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
#	cp -vf $(RC_FILES) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -rvf $(TOOL_DIR) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)
	cp -rvf $(ICONS_DIR) $(HOME)/.qgis2/python/plugins/$(PLUGINNAME)

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/.qgis2/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean 
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis2/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)
