import os
import sys
import pty
import logging
import subprocess

from brainflow_emulator.emulate_common import TestFailureError, Listener


def write (port, data):
    return os.write (port, data)

def read (port, num_bytes):
    return os.read (port, num_bytes)

def get_ports_pty ():
    master, slave = pty.openpty ()
    s_name = os.ttyname (slave)
    m_name = os.ttyname (master)
    return master, slave, m_name, s_name

def test_serial (cmd_list, master, slave, m_name, s_name):
    listen_thread = Listener (master, write, read)
    listen_thread.daemon = True
    listen_thread.start ()

    cmd_to_run = cmd_list + [s_name]
    logging.info ('Running %s' % ' '.join ([str (x) for x in cmd_to_run]))
    process = subprocess.Popen (cmd_to_run, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout, stderr = process.communicate ()

    logging.info ('stdout is: %s' % stdout)
    logging.info ('stderr is: %s' % stderr)

    if process.returncode != 0:
        raise TestFailureError ('Test failed with exit code %s' % str (process.returncode), process.returncode)

    return stdout, stderr

def main (cmd_list):
    if not cmd_list:
        raise Exception ('No command to execute')
    master, slave, m_name, s_name = get_ports_pty ()
    test_serial (cmd_list, master, slave, m_name, s_name)


if __name__=='__main__':
    logging.basicConfig (level = logging.INFO)
    main (sys.argv[1:])
