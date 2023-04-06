import dpkt
from dpkt.compat import compat_ord
from dpkt.udp import UDP
from dpkt.tcp import TCP
import socket
import csv
import os

FILENAMES = ['test.pcap']

# helpers
def write_to_csv(output: dict, filename: str, fieldnames: list):
    file = open(filename, 'w')
    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )
    writer.writeheader()
    writer.writerows(output)
    file.close()


def mac_addr(address):
    """Convert a MAC address to a readable/printable string

       Args:
           address (str): a MAC address in hex form (e.g. '\x01\x02\x03\x04\x05\x06')
       Returns:
           str: Printable/readable MAC address
    """
    return ':'.join('%02x' % compat_ord(b) for b in address)


def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

# grab pcap + do work


def handle_pcap(filename: str):
    safe_file = filename.split('.')[:-1]
    safe_file = '_'.join(safe_file)
    # make output directory for each task
    if not os.path.exists(f'{safe_file}-out'):
        os.mkdir(f'{safe_file}-out')

    output = {}
    output_csv = []
    output_csv_reduced = []
    file = open(filename, 'rb')
    pcap = dpkt.pcap.Reader(file)
    for timestamp, buf in pcap:

        # Unpack the Ethernet frame (mac src/dst, ethertype)
        eth = dpkt.ethernet.Ethernet(buf)

        # Make sure the Ethernet frame contains an IP packet
        if isinstance(eth.data, dpkt.ip.IP):

            # Now access the data within the Ethernet frame (the IP packet)
            # Pulling out src, dst, length, fragment info, TTL, and Protocol
            ip = eth.data
            transport = ip.data

            # add src/dst/port combos to the output dict + track count of each
            if (isinstance(transport, TCP) or isinstance(transport, UDP)):
                gist = f'{inet_to_str(ip.src)}:{inet_to_str(ip.dst)}:{transport.dport}'
                if gist in output:
                    output[gist] += 1
                else:
                    output[gist] = 1

    # create csv output
    for k, v in output.items():
        output_csv.append({
            'src_dst_port': k,
            'count': v
        })
        if v > 4:
            output_csv_reduced.append({
                'src_dst_port': k,
                'count': v
            })

    output_csv = sorted(output_csv, key=lambda d: d['count'], reverse=True)
    output_csv_reduced = sorted(output_csv_reduced, key=lambda d: d['count'], reverse=True)

    # write csv output
    write_to_csv(
        output=output_csv,
        filename=f'{safe_file}-out/src-dst-port.csv',
        fieldnames=[
            'src_dst_port',
            'count'
        ])
    
    # write csv output
    write_to_csv(
        output=output_csv_reduced,
        filename=f'{safe_file}-out/src-dst-port-reduced.csv',
        fieldnames=[
            'src_dst_port',
            'count'
        ])


if __name__ == '__main__':
    for filename in FILENAMES:
        handle_pcap(filename=filename)
