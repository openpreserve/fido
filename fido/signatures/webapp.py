#!/usr/bin/env python
# coding=UTF-8
#
# E-ARK Validation
# Copyright (C) 2019
# All rights reserved.
#
# Licensed to the E-ARK project under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The E-ARK project licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
"""
E-ARK : Information Package REST Validation.

Initialisation module for package, kicks of the flask app.
"""
import logging
__version__ = '0.0.1'
# Load the application
from flask import Flask
APP = Flask(__name__)

from .config import configure_app # pylint: disable-msg=C0413
# Get the appropriate config
configure_app(APP)

# Configure logging across all modules
logging.basicConfig(filename=APP.config['LOG_FILE'], level=logging.DEBUG,
                    format=APP.config['LOG_FORMAT'])
logging.info("Started FIDO Flask application.")
logging.debug("Configured logging.")

# Import the application routes
logging.info("Setting up application routes")
from .controller import ROUTES # pylint: disable-msg=C0413, W0611
