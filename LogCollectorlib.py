# Based on the ips, detect if its a chromeos system. If so, collect the logs and the version details.
# extract logs and rename files to add an extension to it.
# Copy the ready files into corresponding elasticsearch folder
import os
import platform
import paramiko
import re

class LogCollectorlib(object):

    def check_if_remote_system_is_live(self, ip):
        hostname = ip
        try:
            response = os.system("ping -c 1 " + hostname)
        except:
            return False

        if response == 0:
            return True
        else:
            return False

    def run_command_to_check_non_zero_exit_status(self, command, dut_ip, username = "root", password = "test0000"):
        if self.check_if_remote_system_is_live(dut_ip):
            print ("command is %s" % command)
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(dut_ip, username= username, password= password)
                stdin, stdout, stderr = client.exec_command(command)
                command_exit_status = stdout.channel.recv_exit_status()
                out = stdout.read().decode('ascii').strip("\n")
                print ('This is output =', stdout.read())
                print ('This is error =', stderr.read())

                """
                while not stdout.channel.exit_status_ready():
                        # Only print data if there is data to read in the channel
                        if stdout.channel.recv_ready():
                        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                        if len(rl) > 0:
                               # Print data from stdout
                                print stdout.channel.recv(1024),
            
                print "Command done."
                """
                client.close()
                print ("out is: ", out)
                if command_exit_status == 0:
                    print ("exis status is 0")
                    return out
                else:
                    # print "not able to run the command remotely"
                    return False
            except paramiko.ssh_exception.NoValidConnectionsError as error:
                print("Failed to connect to host '%s' with error: %s" % (dut_ip, error))
            except paramiko.AuthenticationException as error:
                print("Failed to authenticate dut '%s' with error: %s" % (dut_ip, error))
            except EOFError:
                print ("Failed EOFError")

        return False

    def check_if_system_is_a_chrome_os_system(self, ip):
        chromeos_detection_cmd = "cat /etc/lsb-release | grep -i chromeos_release_name"
        output = self.run_command_to_check_non_zero_exit_status(chromeos_detection_cmd, ip)
        if output:
            print (output)
            chrome_os_check = re.findall("chrome os|chromium os", output, re.I)
        else:
            return False

        if chrome_os_check:
            return True
        else:
            return False


    def search_and_copy_file_from_dut(self, ip, filename):
        if self.check_if_remote_system_is_live(ip):
            if self.check_if_system_is_a_chrome_os_system(ip):
                print ("Deleting existing generate_log file if any.")
                log_file_path = "/tmp/" + ip + "_generate_log.tgz"
                if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                    self.run_command_to_check_non_zero_exit_status("rm -rf " + log_file_path, ip)

                cmd = "generate_logs --output=" + log_file_path
                generate_log_status = self.run_command_to_check_non_zero_exit_status(cmd, ip)
                print ("generate_log_status is:", generate_log_status)
                if generate_log_status == False:
                    print ("log generation failed")
                    return False
                else:
                    print ("log generated successfuly")
                    if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                        return log_file_path
            else:
                print ("remote system is not a chromeos device")

        else:
            print ("DUT %s is not up" % ip)

        return False


    def collect_chromeos_dut_logs(self, ip):
        if self.check_if_remote_system_is_live(ip):
            if self.check_if_system_is_a_chrome_os_system(ip):
                print ("Deleting existing generate_log file if any.")
                log_file_path = "/tmp/" + ip + "_generate_log.tgz"
                if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                    self.run_command_to_check_non_zero_exit_status("rm -rf " + log_file_path, ip)

                cmd = "generate_logs --output=" + log_file_path
                generate_log_status = self.run_command_to_check_non_zero_exit_status(cmd, ip)
                print ("generate_log_status is:", generate_log_status)
                if generate_log_status == False:
                    print ("log generation failed")
                    return False
                else:
                    print ("log generated successfuly")
                    if self.run_command_to_check_non_zero_exit_status("ls -l " + log_file_path, ip):
                        return log_file_path
            else:
                print ("remote system is not a chromeos device")

        else:
            print ("DUT %s is not up" % ip)

        return False

    def copy_file_from_dut_to_host(self, src, dst, dut_ip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(dut_ip, username='root', password='test0000')

        sftp = client.open_sftp()
        sftp.get(src, dst)
        sftp.close()

        if os.path.isfile(dst):
            print ("File copy successfull")
            return True
        else:
            print ("File copy unsuccessfull")
            return False


