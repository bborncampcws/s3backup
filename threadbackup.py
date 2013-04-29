import paramiko, base64, yaml
import threading

class S3Backup():
  entries=yaml.load(open('./servers.yaml'))

  def start_backup(self):
    for k in self.entries.keys():
      options={}
      options['sudo_cmd']=''
      if self.entries[k].get('sudo',''):
        options['sudo_cmd']='sudo'
      options['source_host']=self.entries[k].get('host','')
      options['password']=self.entries[k].get('password','')
      options['username']=self.entries[k].get('username','')
      options['mysql_location']=self.entries[k].get('mysqldump','')
      options['mysql_password']=self.entries[k].get('mysql_password','')
      options['mysql_username']=self.entries[k].get('mysql_username','')
      options['rsync_flags']='-arv'
      options['file_list']='/etc/backup_file_list' 
      options['backup_host']='63.164.138.22'
      options['server']=k
      print (options['source_host'],options['username'],options['password'])  
      agent=SSHAgent(options)
      agent.start()

class SSHAgent(threading.Thread):
  def __init__(self,options): 
    threading.Thread.__init__(self)
    self.options=options
    
  def run(self):
    self.client = paramiko.SSHClient()
    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.client.connect(self.options['source_host'],username=self.options['username'], password=self.options['password'])
    if self.options['mysql_location']:
      self.mysql_dump()
    else:
      print 'no mysql dump'
    self.file_backup()
    self.client.close()
  
  def file_backup(self):
    print 'file backup'
    rsync_cmd = "nice -n 10 {} rsync {} --files-from={} --delete / {}::s3backup/{}\n".format(self.options['sudo_cmd'],self.options['rsync_flags'],self.options['file_list'],self.options['backup_host'],self.options['server'])
    print rsync_cmd
    stdin, stdout, stderr = self.client.exec_command(rsync_cmd)
    for line in stdout:
      print '...'+line
    for line in stderr:
      print '...'+line
  
  #dump mysql to location
  def mysql_dump(self):
    print 'mysql backup'
    dump_cmd="mysqldump --user={} --password={} --all-databases -v -r {}/all-databases.sql".format(self.options['mysql_username'],self.options['mysql_password'],self.options['mysql_location']) 
    stdin, stdout, stderr = self.client.exec_command(dump_cmd) 
    for line in stdout:
      print '...'+line
    for line in stderr:
      print '...'+line

b=S3Backup()
b.start_backup()
