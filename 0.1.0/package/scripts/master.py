import sys
from resource_management import *
class Master(Script):

  def install(self, env):
    print 'Install the ESMonitor Master';
    self.install_packages(env)
    Execute("yum -y install python-requests.noarch") #putting it as a dependency in the metainfo.xml wasn't working
    if not os.path.exists("/var/log/esmonitor"):
      print("No /var/log/esmonitor - creating")
      try:
        os.makedirs("/var/log/esmonitor")
        print("success creating /var/log/esmonitor")
      except:
        print("creating /var/log/esmonitor failed")
    print("done with custom installation step")

  def stop(self, env):
    try:
      print("killing process")
      f = open("/tmp/esmonitor.pid", "r")
      os.kill(int(f.read()), signal.SIGTERM)
      print("process killed")
    except IOError:
      print("pid file non-existent, no process to kill")
    except OSError:
      print("process not running - continuing")
    try:
      os.unlink("/tmp/esmonitor.pid")
      print("pid file unlinked")
    except OSError:
      print("no pid file to unlink")

  def start(self, env):
    print 'Start the Elastic monitor';
    all_configs = Script.get_config()
    #print(all_configs)
    config = all_configs['configurations']['esmonitor-config']
    metrics_host = all_configs['clusterHostInfo']['metrics_collector_hosts'][0]
    call_list = ["python",
        "/var/lib/ambari-agent/cache/common-services/ESMONITOR/0.1.0/package/scripts/esmonitor.py",
        str(config['check_interval']), metrics_host, str(config['port']),
        config['elastic_username'], config['elastic_password'],
        config['elastic_url']] + config['nodes'].split()
    call(call_list, wait_for_finish=False, logoutput=True,
            stdout='/var/log/esmonitor/esmonitor.out',
            stderr='/var/log/esmonitor/esmonitor.err')

  def status(self, env):
    check_process_status("/tmp/esmonitor.pid")

  def configure(self, env):
    print 'Configure the ESMonitor Master';

  def service_check(self, env):
    print 'Service check the ESMonitor';

if __name__ == "__main__":
  Master().execute()
