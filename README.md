# podman-clamav-el6

Builds the **clamav-0.103.4-1** rpms for Centos 6 systems

I modified the clamav-0.103.4-1 Centos 7 SRPM and made it compatible for Centos 6 systems.  
All clamav RPMs build except for clamav-data, which I had to remove due to the size of the cvd files it contained.  
It's not really needed anyway, just pull in the latest definitions via ```freshclam``` after installation.

**Fedora package install**
```
dnf install podman python3-podman python3-pydbus python3-termcolor
```

**to build**
```
# create podman image and run the container
# run script as a normal user, not as root
./script-podman.py

# then login to the container with:
podman exec -it clamav_builder_6 /bin/bash

# copy rpms to shared volume output_rpms/
./01.copy.rpms.to.output_rpm.sh

# logout of the container with 
Control+D or exit

# the RPM's will now be found in output_rpms/

[leif.liddy@black podman-clamav-el6]$ ll output_rpm/
total 7492
-rw-r--r--. 1 leif.liddy leif.liddy 3125924 Dec 12 03:36 clamav-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy 3304636 Dec 12 03:36 clamav-debuginfo-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy   49992 Dec 12 03:36 clamav-devel-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy   42396 Dec 12 03:36 clamav-filesystem-0.103.4-1.el6.noarch.rpm
-rw-r--r--. 1 leif.liddy leif.liddy  810496 Dec 12 03:36 clamav-lib-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy   84080 Dec 12 03:36 clamav-milter-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy  123496 Dec 12 03:36 clamav-update-0.103.4-1.el6.x86_64.rpm
-rw-r--r--. 1 leif.liddy leif.liddy  114148 Dec 12 03:36 clamd-0.103.4-1.el6.x86_64.rpm
```
