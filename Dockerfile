FROM registry.centos.org/centos:6

ENV clamav_srpm clamav-0.103.4-1.el6.src.rpm

COPY files/bashrc /root/.bashrc
COPY files/*.repo /etc/yum.repos.d
COPY files/RPM-GPG-KEY-EPEL-6 /tmp
COPY files/$clamav_srpm /root

RUN rm -f /etc/yum.repos.d/CentOS-* &&\
    yum update -y &&\
    yum install -y rpm-build rsync vim-enhanced wget yum-utils &&\
    mkdir /root/.bashrc.d /tmp/cmake  &&\
    rpm --import /tmp/RPM-GPG-KEY-EPEL-6 &&\
    yum-builddep -y /root/$clamav_srpm &&\
    yum clean all &&\
    find /root/ -type f | egrep 'anaconda-ks.cfg|install.log|install.log.syslog' | xargs rm -f

COPY files/bashrc-rpmbuild /root/.bashrc.d/rpmbuild

# set login directory
WORKDIR /root

CMD ["/bin/bash"]
