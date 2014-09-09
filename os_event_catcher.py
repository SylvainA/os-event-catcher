#!/usr/bin/env python
#
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Author: Sylvain Afchain <sylvain.afchain@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import eventlet
import socket
import yaml

from oslo.config import cfg

from openstack.common import log as logging
from openstack.common import processutils
from openstack.common.rpc import service
from openstack.common import service as os_service

LOG = logging.getLogger(__name__)

PRODUCT_NAME = 'os-event-catcher'
OPTS = [
    cfg.IntOpt(
        'workers',
        default=8,
        help='How many workers used to catch and trigger script.'),
    cfg.StrOpt(
        'rules_file',
        help='Path to the rules yaml file.'),
]


class OnEventAgent(service.Service):

    def __init__(self, host, topic):
        super(OnEventAgent, self).__init__(host, topic)

        with open(cfg.CONF.OS_EVENT_CATCHER.rules_file) as f:
            self.rules = yaml.load(f)

    def get_value(self, notification, keys):
        if not keys:
            return notification

        key = keys.pop(0)
        return self.get_value(notification[key], keys)

    def process_notification(self, notification):
        LOG.debug(notification)

        for rule in self.rules:
            try:
                keys = rule['path'].split('.')
                value = self.get_value(notification, keys)
                if not value or value != rule['value']:
                    continue

                cmd = [rule['cmd']]
                for arg in rule['args']:
                    keys = arg.split('.')
                    arg_value = self.get_value(notification, keys)
                    cmd.append(arg_value)

                LOG.info(cmd)
                processutils.execute(' '.join(cmd), shell="/bin/sh")
            except:
                pass

    def initialize_service_hook(self, service):
        topic = 'notifications.info'
        try:
            self.conn.join_consumer_pool(
                callback=self.process_notification,
                pool_name=topic,
                topic=topic,
                exchange_name='neutron',
                ack_on_error=True)
        except Exception:
            LOG.exception(_('Could not join consumer pool'
                            ' %(topic)s/%(exchange)s') %
                          {'topic': topic,
                           'exchange': 'neutron'})


def main():
    LOG.debug("Starting....")
    eventlet.monkey_patch()

    server = OnEventAgent(socket.gethostname(), PRODUCT_NAME)
    launcher = os_service.ProcessLauncher()
    launcher.launch_service(server, workers=cfg.CONF.OS_EVENT_CATCHER.workers)
    launcher.wait()


if __name__ == "__main__":

    cfg.CONF(project=PRODUCT_NAME)
    cfg.CONF.register_opts(OPTS, "OS_EVENT_CATCHER")
    logging.setup(PRODUCT_NAME)
    main()
