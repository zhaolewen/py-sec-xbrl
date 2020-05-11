from pysecxbrl.parsing import SECParser

parser = SECParser()

with open('temp-data/0001564590-20-023322-xbrl/geos-20200331.xml') as f:
    txt = f.read()
    res = parser.parseMainXBRL(txt)

    print("parsing result: ")
    print(res)
