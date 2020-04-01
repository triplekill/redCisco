# redCisco
redCisco is red team tool used for Cisco IOS post-exploitation pivoting.  The tool leverages the Cisco IOS TCL scripting shell to run ping scans, both TCP and UDP port scans, and both SOCKS4 proxy and host pivoting through the Cisco device.

## What does it do?
This tool will allow an attacker to setup a SOCKS4 proxy on the compromised Cisco IOS device, providing the attacker with full access to the networks configured on the target device.  By using a tool like "proxychains", its possible to achieve lateral movement within the target network within minutes without having to write your own Cisco commands to redirect traffic.
