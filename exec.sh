#!/bin/bash

if [ -z "$3" ]; then
  echo "A floating IP has been detached" >> /opt/enovance/os-event-catcher/floating
  echo "Tenant ID was: $1, floating IP was: $2" >> /opt/enovance/os-event-catcher/floating
  echo "" >> /opt/enovance/os-event-catcher/floating
else
  echo "A floating IP has been attached" >> /opt/enovance/os-event-catcher/floating
  echo "Tenant ID is: $1, floating IP is: $2 and port ID is $3" >> /opt/enovance/os-event-catcher/floating
  echo "" >> /opt/enovance/os-event-catcher/floating
fi
