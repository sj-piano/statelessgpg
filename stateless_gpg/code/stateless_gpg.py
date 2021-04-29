# Imports
import os
import shutil
import uuid
import subprocess
import logging





# Relative imports
from .. import util




# Shortcuts
join = os.path.join
v = util.validate




# Set up logger for this module. By default, it produces no output.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.ERROR)
log = logger.info
deb = logger.debug




# Notes:
# - Some GPG commands send output to stderr. Use 2>&1 to redirect this output to stdout.





def setup(
    log_level = 'error',
    debug = False,
    log_timestamp = False,
    log_filepath = None,
    ):
  # Configure logger for this module.
  util.module_logger.configure_module_logger(
    logger = logger,
    logger_name = __name__,
    log_level = log_level,
    debug = debug,
    log_timestamp = log_timestamp,
    log_filepath = log_filepath,
  )
  deb('Setup complete.')




class gpg(object):


  # This is a wrapper class. It's meant to be treated as if it were a module. Example:
  # from stateless_gpg import gpg
  # signature = gpg.make_signature(private_key, data)




  def __init__(self):
    pass




  @staticmethod
  def make_signature(private_key, data):
    gpg_dir_name = create_temp_directory()
    data_dir_name = create_temp_directory()
    private_key_file = join(data_dir_name, 'private_key.txt')
    with open(private_key_file, 'w') as f:
      f.write(private_key)
    data_file = join(data_dir_name, 'data.txt')
    with open(data_file, 'w') as f:
      f.write(data)
    permissions_cmd = 'chmod 700 {g}'.format(g=gpg_dir_name)
    run_local_cmd(permissions_cmd)
    import_cmd = 'gpg --no-default-keyring --homedir {g} --import {p} 2>&1'.format(g=gpg_dir_name, p=private_key_file)
    run_local_cmd(import_cmd)
    signature_file = join(data_dir_name, 'signature.txt')
    sign_cmd = 'gpg --no-default-keyring --homedir {g} --output {s} --armor --detach-sign {d}'.format(g=gpg_dir_name, s=signature_file, d=data_file)
    run_local_cmd(sign_cmd)
    signature = open(signature_file).read()
    shutil.rmtree(gpg_dir_name)
    shutil.rmtree(data_dir_name)
    return signature




  @staticmethod
  def verify_signature(public_key, data, signature):
    # Example GPG output: Bad signature
      # gpg: no valid OpenPGP data found.
      # [GNUPG:] NODATA 1
      # [GNUPG:] NODATA 2
      # gpg: the signature could not be verified.
      # Please remember that the signature file (.sig or .asc)
      # should be the first file given on the command line.
    # Example GPG output: Good signature
      # [GNUPG:] SIG_ID m6uSV9RYxObc294UbLSUetwlHJw 2020-08-08 1596924121
      # [GNUPG:] GOODSIG 3375AE2D255344FE Test Key 1
      # gpg: Good signature from "Test Key 1"
      # [GNUPG:] VALIDSIG F90F200288C86F686D65E58C3375AE2D255344FE 2020-08-08 1596924121 0 4 0 1 2 00 F90F200288C86F686D65E58C3375AE2D255344FE
      # [GNUPG:] TRUST_UNDEFINED
      # gpg: WARNING: This key is not certified with a trusted signature!
      # gpg:          There is no indication that the signature belongs to the owner.
      # Primary key fingerprint: F90F 2002 88C8 6F68 6D65  E58C 3375 AE2D 2553 44FE
    gpg_dir_name = create_temp_directory()
    data_dir_name = create_temp_directory()
    public_key_file = join(data_dir_name, 'public_key.txt')
    with open(public_key_file, 'w') as f:
      f.write(public_key)
    data_file = join(data_dir_name, 'data.txt')
    with open(data_file, 'w') as f:
      f.write(data)
    signature_file = join(data_dir_name, 'signature.txt')
    with open(signature_file, 'w') as f:
      f.write(signature)
    permissions_cmd = 'chmod 700 {g}'.format(g=gpg_dir_name)
    run_local_cmd(permissions_cmd)
    import_cmd = 'gpg --no-default-keyring --homedir {g} --import {p} 2>&1'.format(g=gpg_dir_name, p=public_key_file)
    run_local_cmd(import_cmd)
    verify_cmd = 'gpg --no-default-keyring --homedir {g} --status-fd 1 --verify {s} {d} 2>&1'.format(g=gpg_dir_name, s=signature_file, d=data_file)
    output = run_local_cmd(verify_cmd)
    shutil.rmtree(gpg_dir_name)
    shutil.rmtree(data_dir_name)
    result = False
    for line in output.split('\n'):
      if 'gpg: Good signature from' in line:
        result = True
        break
    return result




def create_temp_directory():
  # Start the directory name with a dot so that it's hidden.
  def new_dir_name():
    random_digits = str(uuid.uuid4())[-10:]
    return '.stateless_gpg_' + random_digits
  while True:
    name = new_dir_name()
    if not os.path.exists(name):
      break
  os.mkdir(name)
  return name




def run_local_cmd(cmd):
  proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = proc.communicate()
  out = out.decode('ascii')
  err = err.decode('ascii')
  if err != '':
    msg = 'COMMAND FAILED\n' + '$ ' + cmd + '\n' + err
    stop(msg)
  return out




def stop(msg=''):
  raise Exception(msg)



