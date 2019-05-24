import argparse
import os
import sys
import time
import tarfile
from LogCollectorlib import LogCollectorlib

import subprocess
import shlex
from collections import defaultdict
from scapy.all import srp, Ether, ARP, conf


dest_location = "/media/cssdesk/elk_data/temp_pre_processed_logs"
elk_dest_location = "/media/cssdesk/elk_data/elk_log_source/system_logs"
dest_location_with_timestamp = dest_location + "/" + time.strftime("%Y-%b-%d-%H%M%S")
elk_dest_location_with_timestamp = elk_dest_location + "/" + time.strftime("%Y-%b-%d-%H%M%S")

def is_tool(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


def extract(pattern, tar_url, extract_path='/media/cssdesk/elk_data/elk_log_source', rename_to_txt = False):
    print (tar_url)
    # tar = tarfile.open(tar_url)
    with tarfile.open(tar_url) as tar:
        for member in tar.getmembers():
            if pattern in member.name:
                print (member.name)
                member.name = os.path.basename(member.name)

                tar.extract(member, extract_path)
                if rename_to_txt:
                    filename = extract_path + "/" + member.name
                    new_filename = filename + ".txt"
                    os.rename(filename, new_filename)


if __name__ == "__main__":

    #CHECK if destination folder exist else exit
    if not os.path.isdir(dest_location):
        print ("Destination folder not available. Create one and rerun the log_collector. Exiting tests!")			
        sys.exit()

    try:
        #os.system("mkdir -p " + dest_location_with_timestamp)
        os.mkdir(dest_location_with_timestamp)
    except IOError as (errno, strerror):
        print ("I/O error({0}): {1}".format(errno, strerror))
        sys.exit(1)
    except OSError as e:
        print ("Exception found!!!")
        print (e)
        sys.exit(1)

    #START IP list given from the cmd line
    parser = argparse.ArgumentParser()
    parser.add_argument('--IP', dest='ip_addresses', help='provide remote system ip/s', nargs='+')
    args = parser.parse_args()

    if args.ip_addresses:
        ip_list = args.ip_addresses
    else:
        ip_list = False
        print ("check --help or give cmd argument --IP <ip_address>")
        sys.exit(1)
    print (ip_list)
    # END IP list given from the cmd line


    print (ip_list)

    test = LogCollectorlib()
    for i in ip_list:
        log_status = False
        if test.check_if_remote_system_is_live(i):
            generate_log_status = test.collect_chromeos_dut_logs(i)
            print ("generate_log_status is:", generate_log_status)
            if generate_log_status:
                dst_path = dest_location_with_timestamp + "/" + i + ".tgz"
                if test.copy_file_from_dut_to_host(generate_log_status, dst_path, i):
                    log_status = True
                    tar_url = dst_path
                    extract_path = elk_dest_location_with_timestamp + "/" + i
                    extract("messag", tar_url, extract_path = extract_path, rename_to_txt=True)
                    extract("eventlog.txt", tar_url, extract_path=extract_path)


        if not log_status:
            file = dest_location_with_timestamp + "/" + "error_" + i + ".txt"
            with open(file, "w") as f:
                f.write("not able to copy logs successfully.")
