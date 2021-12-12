#!/usr/bin/python3

import argparse
import dbus
import os
import rpm
import subprocess
import sys
from podman import PodmanClient
from termcolor import cprint


centos_release = '6'

podman_image_name     = 'clamav_rpmbuild_env:' + centos_release
podman_container_name = 'clamav_builder_' + centos_release
container_hostname    = 'clam_builder'


def print_yes():
    cprint(' {}'.format('[YES]'), 'green')


def print_no():
    cprint(' {}'.format('[NO]'), 'red')


def print_success():
    cprint(' {}'.format('[SUCCESS]'), 'green')


def print_failure():
    cprint(' {}'.format('[FAILURE]'), 'red')


def check_podman_installed():
    cprint('{0:.<70}'.format('PODMAN: is podman installed'), 'yellow', end='')
    podman_installed = False
    ts = rpm.TransactionSet()
    rpm_listing = ts.dbMatch()

    for rpm_pkg in rpm_listing:
        if rpm_pkg['name'] == 'podman':
            podman_installed = True

    if podman_installed:
        print_yes()
    else:
        print_no()
        cprint('\npodman is not installed', 'magenta')
        cprint('Exiting...', 'red')
        sys.exit(1)


def ensure_podman_socket_running():
    # system-level = SystemBus
    #bus = dbus.SystemBus()
    # user-level = SessionBus, equivalent of running
    # systemctl --user start podman.socket
    bus = dbus.SessionBus()
    systemd = bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')
    service = 'podman.socket'

    try:
       manager.RestartUnit(service, 'fail')
    except:
       sys.exit('Error: Failed to restart {}.'.format(service))


def ensure_image_exists():
    cprint('{0:.<70}'.format('PODMAN: checking if image exists'), 'yellow', end='')
    podman_image = client.images.list(filters = { 'reference' : podman_image_name})

    if podman_image:
        print_yes()
    else:
        print_no()
        cprint('PODMAN: building image...', 'yellow')
        cur_dir = os.path.dirname(os.path.realpath(__file__))

        if args.debug:
            podman_build_image_manual = 'podman build -t {} .'.format(podman_image_name)
            cprint('DEBUG: to manually build the image:', 'yellow')
            cprint('{}'.format(podman_build_image_manual), 'yellow', attrs=['bold'])

        cmd_output = subprocess.run(['podman', 'build', '--squash', '-t', podman_image_name, cur_dir], universal_newlines=True)

        cprint('{0:.<70}'.format('PODMAN: build image'), 'yellow', end='')
        if cmd_output.returncode != 0:
            print_failure()
            cprint('Exiting...', 'red')
        else:
            print_success()


def ensure_image_removed():
    cprint('{0:.<70}'.format('PODMAN: checking if image exists'), 'yellow', end='')
    podman_image_exists = client.images.list(filters = { 'reference' : podman_image_name})

    if podman_image_exists:
        print_yes()
        cprint('PODMAN: removing image...', 'yellow')
        client.images.remove(image=podman_image_name)
    else:
        print_no()


def ensure_container_exists_and_running():
    cprint('{0:.<70}'.format('PODMAN: checking if container exists'), 'yellow', end='')
    container_exists = client.containers.list(all=True, filters = { "name" : podman_container_name})

    if container_exists:
        print_yes()
        podman_container = client.containers.get(podman_container_name)
        container_status = podman_container.status

        cprint('{0:.<70}'.format('PODMAN: checking if container is running'), 'yellow', end='')

        if container_status == 'running':
            print_yes()
        else:
            print_no()
            cprint('PODMAN: starting container...', 'yellow')
            podman_container.start()
            ensure_container_exists_and_running()
    else:
        print_no()
        run_container()
        ensure_container_exists_and_running()


def create_mounts_dict(host_mount, container_mount):
    mounts = {
               'type':   'bind',
               'source': host_mount,
               'target': container_mount,
             }

    return mounts


def ensure_container_stopped_removed(remove_container=True):
    cprint('{0:.<70}'.format('PODMAN: checking if container exists'), 'yellow', end='')
    container_exists = client.containers.list(all=True, filters = {'name' : podman_container_name})

    if container_exists:
        print_yes()
        podman_container = client.containers.get(podman_container_name)
        container_status = podman_container.status

        cprint('{0:.<70}'.format('PODMAN: checking if container is running'), 'yellow', end='')

        if container_status != 'exited':
            print_yes()
            cprint('PODMAN: stopping container...', 'yellow')
            podman_container.stop()
        else:
            print_no()

        if remove_container:
            cprint('PODMAN: removing container...', 'yellow')
            podman_container.remove()

    else:
        print_no()


def run_container():
    cprint('PODMAN: run container...', 'yellow')
    bind_volumes              = []
    cur_dir                   = os.path.dirname(os.path.realpath(__file__))
    output_rpm_dir_host       = cur_dir + '/output_rpm'
    output_rpm_dir_container  = '/output_rpm'

    bind_volumes.append(create_mounts_dict(output_rpm_dir_host, output_rpm_dir_container))

    if args.debug:
        podman_run_cmd_manual = 'podman run -d -it --privileged=true -v $(pwd)/output_rpm:/root/output_rpm -h {} --name {} {}\n'.format(container_hostname, podman_container_name, podman_image_name)
        cprint('DEBUG: to manually run the container:', 'yellow')
        cprint('{}'.format(podman_run_cmd_manual), 'yellow', attrs=['bold'])

    client.containers.run(image=podman_image_name, name=podman_container_name, hostname=container_hostname, detach=True, tty=True, privileged=True, mounts=bind_volumes)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('--debug',
                        action='store_true',
                        help='display debug messages',
                        default=False)
    group.add_argument('--rebuild',
                        action='store_true',
                        help='remove podman image and container if they exist, '
                             'then build (new) podman image and run container',
                        default=False)
    group.add_argument('--rm_image',
                        action='store_true',
                        help='remove podman image and container if they exist',
                        default=False)
    group.add_argument('--rm_container',
                        action='store_true',
                        help='remove container if it exists',
                        default=False)
    group.add_argument('--stop_container',
                        action='store_true',
                        help='stop container if it exists and is running',
                        default=False)

    args = parser.parse_args()


    check_podman_installed()
    ensure_podman_socket_running()
    client = PodmanClient()

    if args.rm_image:
        ensure_container_stopped_removed()
        ensure_image_removed()
        sys.exit()

    if args.rm_container:
        ensure_container_stopped_removed()
        sys.exit()

    if args.stop_container:
        ensure_container_stopped_removed(remove_container=False)
        sys.exit()

    if args.rebuild:
        ensure_container_stopped_removed()
        ensure_image_removed()


    cprint('{0:.<70}'.format('PODMAN: image name'), 'yellow', end='')
    cprint(' {}'.format(podman_container_name), 'cyan')

    ensure_image_exists()

    cprint('{0:.<70}'.format('PODMAN: container name'), 'yellow', end='')
    cprint(' {}'.format(podman_container_name), 'cyan')

    ensure_container_exists_and_running()

    cprint('PODMAN: to login to the container run:', 'yellow')
    cprint('podman exec -it {} /bin/bash\n'.format(podman_container_name), 'green')
