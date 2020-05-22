from pysecxbrl.parsing import SECParser
from pysecxbrl.extract import XBRLExtractor

import os

parser = SECParser()
extractor = XBRLExtractor()

# 'temp-data/0001564590-20-023322-xbrl/geos-20200331.xml'
# temp-data/1002517_20200508-0001002517-20-000034-xbrl/nuan0331202010-q.htm.xml

folder = "temp-data/1002517_20200508-0001002517-20-000034-xbrl/"

files = extractor.identifyFiles(folder)
print(files)

main_data_f = files["main"][0]
calc_f = files["calculation"][0]

with open(os.path.join(folder, calc_f)) as f:
    txt_calc = f.read()
    calc_elems = parser.parseCalculationXML(txt_calc)

    print(calc_elems)

with open(os.path.join(folder, main_data_f)) as f:
    txt = f.read()
    ctx_elems, data_elems  = parser.parseMainXBRL(txt)

    print("parsing result: ")
    print(ctx_elems)
    print(data_elems)
    print(len(ctx_elems))
    print(len(data_elems))
