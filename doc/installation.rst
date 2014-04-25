Installation
============

Dependencies
------------

The following non-python dependencies must be installed for a fully functioning download counter::

    apt-get install lipgeoip1 python-dev


To install the dependencies in a virtualenv, do the following::

    apt-get install python-virtualenv
    virtualenv <tdc_python>
    source <tdc_python>/bin/activate
    pip install -r <tdc>/requirements.txt
