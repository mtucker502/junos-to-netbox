# How to use

Use requirements.txt to install all dependencies.

If necessary manually install junos-tools module with the following command:
```bash
pip install git+https://github.com/mtucker502/junos-tools.git
```

You can then specify a XML file containing a Junos configuration as the first argument:
```bash
./junos-to-netbox.py vsrx.xml
```

There are several dictionaries defined in the beginning of the script. There is currently no easy way to populate these from 
the configuration file so they are hardcoded for now. Change these as needed for different platforms.

# Ansible

Also provided is an Ansible playbooy to demonstrate the capabilities of automatically pulling the configs and 
then importing the interface/IP data into Netbox

# Notes

This script will verify gracefully handle the pre-existence of all required elements and will not duplicate objects (IP addresses as an example).