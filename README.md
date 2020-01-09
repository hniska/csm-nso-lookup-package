# csm-nso-lookup-package

Package that will integrate Cisco Situation Manager with NSO so that Situation Manager can lookup devicename to NSO services. Well in reality you can use it for any lookups but in this example it will populate the Situation Manager event field custom_info.eventDetails.nso with a device to service mapping.

This package contains three pieces, one NSO package that contains a simple YANG list and a subscriber that updates the last-modified time when the list is updated.

```
    list device-to-service {
      description "device to service lookup table";
      key "device";
      leaf device {
            type string;
            tailf:info "";
      }
          leaf-list services {
              type string;
          }
    }
    leaf last-modified {
        type string;
        config false;
        tailf:cdb-oper {
          tailf:persistent true;
        }
    }
```

On the Situation Manager side you have a script (update-lookup.py) that connects to NSO over RESTConf and downloads the device-to-service list (if last-modified has changed) and stores that in a lookup-file (default $MOOGSOFT/config/lookups/device-to-service.lookup). This script can then be run periodically from crontab.

The update-lookup.py script can also run on an internal schedule which is nice when you are doing demoes and for POC as the smallest repeat time for crontab is 1 minute.

The lookup file format

```
{
    "device1": {
        "services": [
            "servicename1",
            "servicename2"
        ]
    }
    "device2": {
        "services": [
            "servicename1",
            "servicename3"
        ]
    }
}
```

There is also an enrichment workflow that reads the lookup file that update-lookup.py creates. Default the lookup file is re-read every 30 seconds. The workflow checks if the device in the alert can be found in the lookup table it populates the custom_info.eventDetails.nso field with the list of services.

## Installation

### NSO

Copy the csm-lookup (it contains the NSO lookup package) folder to the NSO packages folder. Then compile it

```
$> cd packages/csm-lookup/src
$> make
```

And reload NSO packages

```
$> ncs_cli -u admin
> request packages reload
```

### Situation Manager

Make sure you run Situation Manager version 7.3 and has the latest workflow bundle (workflowBundle-v1.0.tar.gz), otherwise the workflow engine will not have the "staticLookup" function.

[update Situation Manager workflow](https://docs.moogsoft.com/en/update-the-workflow-engine.html)

Copy the update-lookup.py somewhere on the Situation Manager server (make sure it has the execute bit set).

```
$> chmod +x update-lookup.py
$> cp update-lookup.py $MOOGSOFT_HOME/contrib/
```

Then either run in from crontab at a resoable schedule or for demo and POC purposes it can also run on an internal scheduler

To run check and update the lookup file every 5 seconds run it as

```
$> update-lookup.py --timer 5
```

To create the workflow run the create-service-lookup-enricher.sh locally on your Situation Manager installtion. The script will create an "Enrichment Workflow" called "NSO Service Lookup".

![workflow1](/workflow1.jpg)
![workflow2](/workflow2.jpg)

## Usage

Have the NSO service template populate the csm-lookup table and then wait for the update-lookup.py script to create the lookup file and the enrichment workflow to reload it.

Add something like this to the service template

```xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <csm-lookup xmlns="http://example.com/csm-lookup">
    <device-to-service>
      <device>{/endpoint/device}</device>
      <services>{/name}</services>
    </device-to-service>
  </csm-lookup>
</config>
```
