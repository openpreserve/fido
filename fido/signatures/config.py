#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FIDO: Format Identifier for Digital Objects.

Copyright 2010 The Open Preservation Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Configuration for FIDO signature Flask app."""
import os.path
import tempfile

from flask_debugtoolbar import DebugToolbarExtension
from .const import ENV_CONF_PROFILE, ENV_CONF_FILE

HOST = 'localhost'

TEMP = tempfile.gettempdir()
HOME = os.path.expanduser('~')
LOG_ROOT = TEMP
UPLOADS_TEMP = os.path.join(TEMP, 'ip-uploads')
class BaseConfig():# pylint: disable-msg=R0903
    """Base / default config, no debug logging and short log format."""
    NAME = 'Default'
    HOST = HOST
    DEBUG = False
    TESTING = False
    LOG_FORMAT = '[%(filename)-15s:%(lineno)-5d] %(message)s'
    LOG_FILE = os.path.join(LOG_ROOT, 'fido-signatures.log')
    SECRET_KEY = 'a5c020ced05af9ad3189304a41beb5c7b6f750b846dadad'
    FIDSIG_ROOT = TEMP

class DevConfig(BaseConfig):# pylint: disable-msg=R0903
    """Developer level config, with debug logging and long log format."""
    NAME = 'Development'
    DEBUG = True
    TESTING = True
    LOG_FORMAT = '[%(levelname)-8s %(filename)-15s:%(lineno)-5d %(funcName)-30s] %(message)s'

class TestConfig(BaseConfig):# pylint: disable-msg=R0903
    """Developer level config, with debug logging and long log format."""
    NAME = 'Testing'

CONFIGS = {
    "dev": 'fido.signatures.config.DevConfig',
    "default": 'fido.signatures.config.BaseConfig',
    "test": 'fido.signatures.config.TestConfig'
}

def configure_app(app, profile_name='dev'):
    """Grabs the environment variable for app config or defaults to dev."""
    config_name = os.getenv(ENV_CONF_PROFILE, profile_name)
    app.config.from_object(CONFIGS[config_name])
    if os.getenv(ENV_CONF_FILE):
        app.config.from_envvar(ENV_CONF_FILE)
    if not os.path.exists(UPLOADS_TEMP):
        os.makedirs(UPLOADS_TEMP)
    DebugToolbarExtension(app)
