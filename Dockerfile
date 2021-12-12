FROM registry.centos.org/centos:6

COPY files/*.repo /etc/yum.repos.d
COPY files/RPM-GPG-KEY-EPEL-6 /tmp
COPY files/clamav-0.103.4-1.el6.src.rpm /root
COPY files/01.copy.rpms.to.output_rpm.sh /root

RUN rm -f /etc/yum.repos.d/CentOS-* &&\
    yum update -y &&\
    yum install -y vim-enhanced rpm-build rsync git wget yum-utils &&\
    wget https://github.com/Kitware/CMake/releases/download/v3.13.5/cmake-3.13.5-Linux-x86_64.tar.gz -O /tmp/cmake.tar  &&\
    mkdir /tmp/cmake  &&\
    tar --strip-components=1 -xvf /tmp/cmake.tar --directory /tmp/cmake  &&\
    chown -R root:root /tmp/cmake  &&\
    rsync -avr /tmp/cmake/share/cmake-3.13 /usr/local/share/  &&\
    rsync -avr /tmp/cmake/bin/ /usr/local/bin/  &&\
    rpm --import /tmp/RPM-GPG-KEY-EPEL-6 &&\
    yum-builddep -y /root/clamav-0.103.4-1.el6.src.rpm &&\
    yum clean all &&\
    sed -i 's/^alias/#&/' /root/.bashrc &&\
    echo -e "\nalias vi='vim'" >> ~/.bashrc &&\
    echo -e "\nalias gospec='cd ~/rpmbuild/SPECS'" >> ~/.bashrc &&\
    echo -e "\nalias gobuild='cd ~/rpmbuild/BUILD'" >> ~/.bashrc &&\
    echo -e "\nalias gosource='cd ~/rpmbuild/SOURCES'" >> ~/.bashrc &&\
    rm -f /root/anaconda-ks.cfg 2> /dev/null &&\
    rm -f /root/install.log 2> /dev/null &&\
    rm -f /root/install.log.syslog 2> /dev/null &&\
    rm -rf /output_rpm/* 2> /dev/null &&\
    rpm -ivh /root/clamav-0.103.4-1.el6.src.rpm &&\
    rpmbuild -ba /root/rpmbuild/SPECS/clamav.spec

WORKDIR /root

CMD ["/bin/bash"]

