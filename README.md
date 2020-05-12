# py-sec-xbrl
SEC EDGAR Parser based on Python 3

# Intruduction
This is a tool intended to parse XBRL files from SEC. Thus, the focus is to parse XBRL XML files so that data is more easily accessible. The idea is to provide a tool for you to code you want instead of a tool that implements a workflow but is rigid.

In addition, it's not intended to be a tool to scrap SEC EDGAR as it varies a lot as to how you want to do the scrapping and it's relatively easier. (though it can be added later if you want)

The repository is originally forked from https://github.com/tooksoi/ScraXBRL, but I soon find out that we have very different approaches and objectives, so soon afterwards the code in the 2 repositories are completely different and nothing is taken from ScraXBRL.

# How to install
Current verion: `v0.1`

Dependencies: in the `requirements.txt` file, currently only the `lxml` library

Installation:
`pip install py-sec-xbrl`

# How to start
1. get some XBRL XML files (see documentation if you don't have one yet)
2. see `test-parse.py`, modify the path to the XML file and it's really easy

# Documentation
More detailed documentation can be found here: [doc](/doc/README.MD)

# Development roadmap
2 priorities for the moment:
1. Basic SEC XBRL parsing capabilities
2. Make the scripts ready as a library that can be installed
