#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2021 Alexander Gailer
#########################################################################
#  This file is part of SmartHomeNG.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import logging
from lib.model.smartplugin import *
from lib.module import Modules
import cherrypy
from lib.utils import Utils
import urllib.request, json
import time
import re
import requests

class Judo(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff
    """
    
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.0.0.0"
    HEADERS = {'user-agent': 'my-judo', "Accept": "*/*", "Content-Type": "application/json"}

    token = None

    def __init__(self, sh, ipaddress, username, password, device_number, port=8124, cycle=60):
        '''
        
        '''
        self.logger.debug('Init plugin (JUDO)')
        
        self._sh = sh
        self.logger = logging.getLogger(__name__)
        
        self.ipaddress = ipaddress
        self.port = int(port)
        self.username = username
        self.password = password
        self.device_number=device_number
        self.cycle = cycle
        
        self.logger.info(f'Init with params ip={self.ipaddress}, port={self.port}, username={self.username}, password={self.password}, device={self.device_number}, cycle={self.cycle}')

        self.cycle = int(cycle)
        self._items = []

        if Utils.is_ip(ipaddress):
            self.ipaddress = ipaddress
        else:
            self.logger.error(str(ipaddress) + " no valid")            

        if not self.init_webinterface():
            self._init_complete = False            

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.debug("run method called (JUDO)")
        self.alive = True
        self.scheduler_add('update', self._refresh, cycle=self.cycle)

    def stop(self):
        """
        Stop method for the plugin
        """

        self.closeConnection()       
        
        self.logger.debug("stop method called (JUDO)")
        self.alive = False

    def get_items(self):
        """
        Returns added items

        :return: array of items hold by the device
        """
        return self._items
    
    def parse_item(self, item):
        """
        Checks all Items with judo_cfg, see readme
        """
        if self.has_iattr(item.conf, 'judo_cfg'):
            self.logger.debug(f"parse_item method called (JUDO): Item={item}")      
            self._items.append(item)
            return self.update_item

    def parse_logic(self, logic):
        """
        Not implemented yet
        """
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Not implemented yet
        """
        pass

    def closeConnection(self):
        """
        Disconenct is performed, Logout is performed
        Token set to None
        """
        self.disconnect()
        self.logout()
        self.token = None

    def login(self):
        """
        Login into device and set's the token
        """
        URL_TOKEN = f"https://{self.ipaddress}:{self.port}/?group=register&command=login&msgnumber=1&name=login&user={self.username}&password={self.password}&role=customer"
                   
        json = self.getJsonFromUrl(URL_TOKEN, self.HEADERS)
        if json == None:
            return False

        status = json['status']
        self.token = ""
        if status == "ok":
            self.token = json['token']
            self.logger.debug(f"Token={self.token}")
            return True
        self.logger.error(f"Error on getting token: Status={status}")
        return False

    def connect(self):
        """
        Connect to the device with requested token and serialnumber
        """
        URL_CONNECT = f"https://{self.ipaddress}:{self.port}/?group=register&command=connect&msgnumber=6&token={self.token}&parameter=i-soft%20plus&serial%20number={self.device_number}"
        json = self.getJsonFromUrl(URL_CONNECT, self.HEADERS)
        if json == None:
            return False

        status = json['status']
        if status == "ok":
            self.logger.debug(f"Connect=ok")
            return True
        self.logger.error(f"Error on connecting. Status={status}")
        return False 

    def logout(self):
        """
        Performs the logout from device
        """
        URL = f"https://{self.ipaddress}:{self.port}/?group=register&command=logout&msgnumber=1&token={self.token}"
        json = self.getJsonFromUrl(URL)
        if json == None:
            return False
        status = json['status']
        if status == "ok":
            self.logger.debug(f"Logout successfull")
            return True
        self.logger.error(f"Error on logout. Status={status}")
        return False 

    def disconnect(self):
        """
        Performs the disconnect from device
        """
        URL = f"https://{self.ipaddress}:{self.port}/?group=register&command=disconnect&msgnumber=1&token={self.token}"
        json = self.getJsonFromUrl(URL)
        if json == None:
            return False
        status = json['status']
        if status == "ok":
            self.logger.debug(f"Disconnect successfull")
            return True
        self.logger.error(f"Error on disconnect. Status={status}")
        return False 
        
    def parseSetting(self, item):
        """
        Parse the configuration per item
        """
        item_setting_json = self.get_iattr_value(item.conf, 'judo_cfg').replace("'", "\"")
        item_setting = json.loads(item_setting_json)
        self.logger.debug(f"Item Setting={item_setting}")
        group = None
        command = None
        msgnumber = None
        factor = 1
        trim_val = False
        
        try:
            if not 'group' in item_setting:
                raise Exception ('Group not configured')
            group = item_setting['group']
            if not 'command' in item_setting:
                raise Exception ('Command not configured')
            command = item_setting['command']
            if not 'msgnumer' in item_setting:
                msgnumber = '1'
            else:
                msgnumber = item_setting['msgnumber']
            if 'factor' in item_setting:
                try:
                    factor = float(item_setting['factor'])
                except Exception as e:
                    self.logger.error(e)
            if 'trim_val' in item_setting:
                try:
                    trim_val = bool(item_setting['trim_val'])
                except Exception as e:
                    self.logger.error(e)
        except Exception as e:
            self.logger.error(e)

        return (group, command, msgnumber, factor, trim_val)

    def getData(self, item):
        """
        Checks if a connect is required then parse the item and retrieve the data and set the data
        """
        if self.token is None:
            if not self.login():
                return
            else:
                if not self.connect():
                    self.token = None
                    return

        group, command, msgnumber, factor, trim_val = self.parseSetting(item)

        if group is None or command is None or msgnumber is None:
            self.logger.error(f"Missing data for request ({group},{command},{msgnumber})")
            return

        URL_DATA = f"https://{self.ipaddress}:{self.port}/?group={group}&command={command}&msgnumber={msgnumber}&token={self.token}"        
        
        data_received = self.getJsonFromUrl(URL_DATA, self.HEADERS)
        status = data_received['status']
        data = data_received['data']
        if status != 'ok':
            self.logger.error(f'Error on GetData {data}, doing disconnect and logout')
            self.closeConnection()
            return

        data = data_received['data']
        # Trims data if configured
        if trim_val:
            data = data.replace(' ', '')
        
        # Factor for the value if given
        if factor != 1:
            data = float(data) * factor
            
        item(data)

    def getJsonFromUrl(self, URL, headers={}):
        self.logger.debug(f"Data URL={URL}")
        try:
            response = requests.get(URL, headers, verify=False)
            self.logger.debug(response)
            # Only HttpCode 200 - 299 is successfully
            if response.status_code < 200 or response.status_code > 299:
                raise Exception(f"Error receiving, Status_code={response.status_code}")    
        except Exception as e:
            self.closeConnection()
            self.logger.error(e)
            return None

        json = response.json()
        self.logger.debug(f"Data_Received (JSON)={json}")
        return json

    def _refresh(self):
        start = time.time()
        # goes to all items and retrieve the data
        for item in self._items:            
            self.getData(item)
        cycletime = time.time() - start
        self.logger.debug("cycle takes {0} seconds".format(cycletime))

    def init_webinterface(self):
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        try:
            self.mod_http = Modules.get_instance().get_module(
                'http')  # try/except to handle running in a core version that does not support modules
        except:
            self.mod_http = None
        if self.mod_http == None:
            self.logger.error("Plugin '{}': Not initializing the web interface".format(self.get_shortname()))
            return False

        # set application configuration for cherrypy
        webif_dir = self.path_join(self.get_plugin_dir(), 'webif')
        config = {
            '/': {
                'tools.staticdir.root': webif_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static'
            }
        }

        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True
# ------------------------------------------
#    Webinterface of the plugin
# ------------------------------------------

class WebInterface(SmartPluginWebIf):

    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface
        
        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.logger = plugin.logger
        self.tplenv = self.init_template_environment()

    @cherrypy.expose
    def index(self, reload=None, action=None):
        """
        Build index.html for cherrypy

        Render the template and return the html file to be delivered to the browser

        :return: contents of the template after beeing rendered
        """
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), plugin_version=self.plugin.get_version(),
                           plugin_info=self.plugin.get_info(), p=self.plugin)
