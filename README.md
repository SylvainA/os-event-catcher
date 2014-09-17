os-event-catcher
================

Trigger scripts on openstack notification events

How to start it
---------------

os-event-catcher --config-file os_event_catcher.conf

Configure neutron
-----------------

Edit `/etc/neutron/neutron-server/conf`:

    notification_topics = notifications, os-event-catchers"

How to write the rules
----------------------

Assuming we have this notification payload:

```
{u'_context_roles': [u'admin', u'heat_stack_owner'], u'_context_request_id': u'req-2b6bdd7a-bb4a-4089-9818-d0f3cf5e7ebd', u'_context_tenant_name': u'demo', u'event_type': u'network.create.start', u'_context_user_name': u'admin', u'_context_project_name': u'demo', u'timestamp': u'2014-09-09 20:34:49.763694', u'_context_auth_token': u'PKIZ', u'_context_user': u'418d36d261714842b1e607060c8d8917', u'_context_tenant': u'34dc39ef69e046e8813bce25d991bb80', u'message_id': u'42f7f93d-e2c8-469e-8c17-a41a8e5fd1b8', u'_unique_id': u'4b84fc17fdfd496389e0da5bd963f5d2', u'_context_is_admin': True, u'_context_timestamp': u'2014-09-09 20:34:49.756454', u'_context_project_id': u'34dc39ef69e046e8813bce25d991bb80', u'_context_tenant_id': u'34dc39ef69e046e8813bce25d991bb80', u'_context_read_deleted': u'no', u'_context_user_id': u'418d36d261714842b1e607060c8d8917', u'publisher_id': u'network.ops', u'payload': {u'network': {u'name': u'dc', u'admin_state_up': True}}, u'priority': u'INFO'}
```

If we want to trigger a script for this specific event, network.create.start, we have to add a rule in the rules yaml file:

```
-
    path: event_type
    value: network.create.start
    cmd: echo
    args:
        - _context_tenant
        - payload.network.name

```

The path field specifies what is the key used in the payload to filter the events. Use a dot separated string to specify a path in the case of the use of subkeys.

The value field is used to filter the event, so here only the field event_type having the value network.create.start will trigger a script.

The cmd field is used to specify the script triggered.

The args field is a list of key/subkey path. The value of the first key will be used as first argument of the script, the second as the second argument and so on.

Below an example with two scripts trigerred:
```
-
    path: event_type
    value: network.create.start
    cmd: echo
    args:
        - _context_tenant
        - payload.network.name
-
    path: event_type
    value: network.create.start
    cmd: touch
    args:
        - _context_tenant
        - payload.network.name

```

Example with floating IPs
-------------------------

At some point, you might like to get notified or to trigger actions on a floating IP event.
The current rule catches any attach or detach floating IP call.
It will execute the "exec.sh" script for each catch, the script will do the rest.
The script simply prints in a file every useful information regarding the floating IP.

Pacemaker config
----------------

    crm configure primitive p_os_event_catcher lsb:os-event-catcher op monitor interval="10s"
