#!/usr/bin/env bash
# Contains common functions for various tasks
# author: Tim Rozet (trozet@redhat.com)

# Installs/Upgrades/downgrades RPMs
# Expects global env variables VERSION_EXTENSION and RPM_LIST are set
# param: VERSION_EXTENSION is the version of the RPMs to be installed, such as
#        "3.0-20150406"
function install_rpms {
  if [ -z "$VERSION_EXTENSION" ]; then
    echo "VERSION_EXTENSION is undefined...exiting"
    exit 1
  fi

  if [ -z "$RPM_LIST" ]; then
    echo "RPM_LIST is undefined...exiting"
    exit 1
  fi

  # update / install the new rpm
  if rpm -q opnfv-apex > /dev/null; then
     INSTALLED_RPMS=$(rpm -qa | grep apex)
     for x in $INSTALLED_RPMS; do
       INSTALLED_RPM_VER=$(echo $x | grep -Eo '[0-9]+\.[0-9]+-[0-9]{8}')
       # Does each RPM's version match the version required for deployment
       if [ "$INSTALLED_RPM_VER" == "$VERSION_EXTENSION" ]; then
         echo "RPM $x is already installed"
       else
         echo "RPM $x does not match version $VERSION_EXTENSION"
         echo "Will upgrade/downgrade RPMs..."
         # Try to upgrade/downgrade RPMS
         if sudo yum update -y $RPM_LIST | grep "does not update installed package"; then
           if ! sudo yum downgrade -y $RPM_LIST; then
             sudo yum remove -y opnfv-apex-undercloud opnfv-apex-common opnfv-apex-opendaylight-sfc opnfv-apex-onos
             if ! sudo yum downgrade -y $RPM_LIST; then
               echo "Unable to downgrade RPMs: $RPM_LIST"
               exit 1
             fi
           fi
         fi
         break
       fi
     done
  else
     sudo yum install -y $RPM_LIST;
  fi
}
