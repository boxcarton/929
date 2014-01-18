929
===

An easy way to know when tickets go on sale on the 930 club website.

The program scrapes a list of concerts sites for new links.  The links are
extracted from the HTML and then filtered through a bloom filter for new links.
The links are then sent to an email of your choice.


Instructions
============

(Work in progress)

1. List of sites to be scraped are hard coded in run_929.py
2. Modify the config file according to 929.example.cfg
3. python run_929.py -c 929.cfg
