#!/usr/bin/env bash
# Contains common functions for various tasks
# author: Tim Rozet (trozet@redhat.com)

# Installs/Upgrades/downgrades RPMs
# Expects global env variables VERSION_EXTENSION, APEX_PKGS, RPM_LIST are set
# variable: VERSION_EXTENSION is the version of the RPMs to be installed, such as
#        "3.0-20150406"
# variable: APEX_PKGS is the list of known apex package variants
# variable: RPM_LIST is the list of RPMs to install
function install_rpms {
  if [ -z "$VERSION_EXTENSION" ]; then
    echo "VERSION_EXTENSION is undefined...exiting"
    exit 1
  fi

  if [ -z "$RPM_LIST" ]; then
    echo "RPM_LIST is undefined...exiting"
    exit 1
  fi

  if [ -z "$APEX_PKGS" ]; then
    echo "APEX_PKGS is undefined...exiting"
    exit 1
  fi

  # Build known APEX RPM List
  APEX_RPMS="opnfv-apex"
  for pkg in ${APEX_PKGS}; do
    APEX_RPMS+=" opnfv-apex-${pkg}"
  done

  # update / install the new rpm
  if rpm -q opnfv-apex > /dev/null; then
     INSTALLED_RPMS=$(rpm -qa | grep apex)
     for x in $INSTALLED_RPMS; do
       INSTALLED_RPM_VER=$(echo $x | grep -Eo '[0-9]+\.[0-9]+-[0-9]{8}')
       # Does each RPM's version match the version required for deployment
       if [ "$INSTALLED_RPM_VER" == "$VERSION_EXTENSION" ]; then
         echo "RPM $x is already installed"
       else
         echo "RPM $x does not match version ${VERSION_EXTENSION}"
         echo "Will upgrade/downgrade RPMs..."
         # Try to upgrade/downgrade RPMS
         if sudo yum update -y $RPM_LIST | grep "does not update installed package"; then
           echo "RPMs to be installed are an older version...attempting downgrade"
           if ! sudo yum downgrade -y $RPM_LIST; then
             echo "Downgrade failed, will remove current and install new RPMs"
             sudo yum remove -y ${APEX_RPMS}
             if ! sudo yum install -y $RPM_LIST; then
               echo "Unable to install new RPMs: $RPM_LIST"
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
