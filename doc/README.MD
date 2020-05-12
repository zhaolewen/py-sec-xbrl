# Documentation
## Table of Contents
1. [List of classes & functions](#class_functions)
1. [Identifying file types](#identify_file_types)
2. [Parsing Output data structure](#output_data_structure)
3. [How to get data](#get_data)

## List of classes & functions <a name="class_functions"></a>

### Package `pysecxbrl.extract`
#### Class `pysecxbrl.extract.XBRLExtractor`

## Identifying file types <a name="identify_file_types"></a>


## Parsing Output data structure <a name="output_data_structure"></a>
The current version will give you 2 dictionaries, one for the data and another for the context.

### Data part:
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

### Context part:
In the current version, 2 types of context are considered:
1. unit of measure (USD, CAD, ...)
2. context: time + segment (time instant/stard & end date, which part of the business or other stakeholders)

##### unit
```python
{"id":{ # the id of the context object
    "type":"unit", # the unit type
    "unit":"...", # value of the unit, e.g. can be USD
    "...":"..." # other attributes are possible
    }
}
```

##### context
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

## How to get data <a name="get_data"></a>
1. The entry point is here: https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm
2. As is mentioned on the page, you can get daily filing lists here: https://www.sec.gov/Archives/edgar/daily-index/
3. Getting into the folders, you can see several types of index files, they are normally the same but organized in different ways, I personally prefer the "master" file
4. The "Master" file is a text file, and every line is like this: `1001115|GEOSPACE TECHNOLOGIES CORP|10-Q|20200508|edgar/data/1001115/0001564590-20-023322.txt`
5. This text file is in fact not the XBRL file, but we can get its folder path: https://www.sec.gov/Archives/edgar/data/1001115
6. And in the inner folder, you can see the XBRL file which is `0001564590-20-023322-xbrl.zip`

![SEC Company Folder](pics/sec_folder.png)
