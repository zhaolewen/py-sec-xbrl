# py-sec-xbrl
SEC EDGAR Parser based on Python 3

# Intruduction
This is a tool intended to parse XBRL files from SEC. Thus, the focus is to parse XBRL XML files so that data is more easily accessible. The idea is to provide a tool for you to code you want instead of a tool that implements a workflow but is rigid.

In addition, it's not intended to be a tool to scrap SEC EDGAR as it varies a lot as to how you want to do the scrapping and it's relatively easier. (though it can be added later if you want)

The repository is originally forked from https://github.com/tooksoi/ScraXBRL, but I soon find out that we have very different approaches and objectives, so soon afterwards the code in the 2 repositories are completely different and nothing is taken from ScraXBRL.

# How to install
Current verion: `v0.1`
Dependencies: in the `requirements.txt` file, currently only the `lxml` library

# How to use
1. get some XBRL XML files (see below if you don't have one yet)
2. see `test-parse.py`, modify the path to the XML file and it's really easy

# Output data structure
The current version will give you 2 dictionaries, one for the data and another for the context.

## Data part:
```python
{"id":{ # the id of the data object
    "tag":"...", # name of the tag, e.g. Revenue, CostOfSales ...
    "value":"...", # value of the tag, current version returns all values in string
    "prefix":"...", # namespace in the XML, e.g. us-gaap, dei, ...
    "contextRef":"..." # the reference ID to the context part
    "...":"..." # here you can have other attributes specific to the data object
    }
}
```

## Context part:
In the current version, 2 types of context are considered:
1. unit of measure (USD, CAD, ...)
2. context: time + segment (time instant/stard & end date, which part of the business or other stakeholders)

#### unit
```python
{"id":{ # the id of the context object
    "type":"unit", # the unit type
    "unit":"...", # value of the unit, e.g. can be USD
    "...":"..." # other attributes are possible
    }
}
```

#### context
```python
{"id":{ # the id of the context object
    "type":"context", # the context type
    "instant":"2020-05-08", # it will be either a date or start+end
    "startDate":"...","endDate":"...",
    "segment":[ # list of one or more stakeholders
      "explicitMember":"...", # the "who"
      "dimension":"..." # can be very diverse
    ],
    "...":"..." # other attributes are possible
    }
}
```

# How to get data
1. The entry point is here: https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm
2. As is mentioned on the page, you can get daily filing lists here: https://www.sec.gov/Archives/edgar/daily-index/
3. Getting into the folders, you can see several types of index files, they are normally the same but organized in different ways, I personally prefer the "master" file
4. The "Master" file is a text file, and every line is like this: `1001115|GEOSPACE TECHNOLOGIES CORP|10-Q|20200508|edgar/data/1001115/0001564590-20-023322.txt`
5. This text file is in fact not the XBRL file, but we can get its folder path: https://www.sec.gov/Archives/edgar/data/1001115
6. And in the inner folder, you can see the XBRL file which is `0001564590-20-023322-xbrl.zip`

![SEC Company Folder](/doc/sec_folder.png)


# Development roadmap
2 priorities for the moment:
1. Basic SEC XBRL parsing capabilities
2. Make the scripts ready as a library that can be installed
