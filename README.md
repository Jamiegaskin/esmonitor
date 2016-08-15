# Elasticsearch shard and node monitor
Linux Elastic monitor built for Ambari integration. Ambari service that checks for unassigned shards and that all nodes in a user list are up and running.

Built and tested on Centos 6.5 and Ambari 2.2.2 with Python 2.6.6

## Installation
From the ambari server host, get the files.
```
git clone https://github.com/Jamiegaskin/esmonitor
```
If you don't have git, it's as easy as `yum install git` on Centos.

Create a directory for the service.
```
mkdir /var/lib/ambari-server/resources/common-services/ESMONITOR
```

Copy the files into place.
```
cp -R filesystem-monitor/ESMONITOR /var/lib/ambari-server/resources/stacks/HDP/<HDP_VERSION>/services
cp -R filesystem-monitor/0.1.0 /var/lib/ambari-server/resources/common-services/ESMONITOR
```

Where HDP_VERSION is your version of HDP (I used 2.4). At this point you should have:
- /var/lib/ambari-server/resources/stacks/HDP/<HDP_VERSION>/services/ESMONITOR
- /var/lib/ambari-server/resources/common-services/ESMONITOR/0.1.0

Restart Ambari Server.
```
ambari-server restart
```

Installation can now be completed by adding the service "ES Monitor".

*Code adapted from Bryan Bende's tutorials and examples*
