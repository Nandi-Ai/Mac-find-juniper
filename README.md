# Juniper Switch MAC address lookup

A code to use LLDP Neighbours to search a network of Juniper switches for mac address.
The username and password of switches is identical in this code and is saved hardcoded.

The code is starting from one swtich and iterate to other switches using their name it finds in LLDP Neighbours
Then it looks it up in the dictionary in the begining of the code

found it super usefull


Nandi Team


## Usage

Be sure to change the configurations and add switches to the dictionary

Install the required dependencies:

```

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python3 find_mac_address.py -m MacAddress

```


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.
