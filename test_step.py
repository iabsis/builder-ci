#!/usr/bin/env python3
# -*- coding: utf-8 -*-

id="60af6018200fca63283f8907"
step="publish"
method="redmine"

import sys
sys.path.append('lib')

import lib.publish.redmine as redmine
from  options import OptionsDb
from options import OptionsYaml
from meta import Meta

redmine.runAction(id, OptionsDb(id, step, method), Meta(id))