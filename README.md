s3backup
========

reads in .yaml file and does a threaded backup to s3

s3 data gets pushed via rsync to an s3fs mount

overview:
  read in .yaml file
	  spawn thread for each server entry
		  ssh to server
			rsync from server to s3fs server
	
while clients are sending data via rsync the s3fs server pushes data to s3
