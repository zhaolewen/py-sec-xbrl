from pysecxbrl.parsing import SECParser

parser = SECParser()

# 'temp-data/0001564590-20-023322-xbrl/geos-20200331.xml'
# temp-data/1002517_20200508-0001002517-20-000034-xbrl/nuan0331202010-q.htm.xml

with open('temp-data/1002517_20200508-0001002517-20-000034-xbrl/nuan0331202010-q.htm.xml') as f:
    txt = f.read()
    ctx_elems, data_elems  = parser.parseMainXBRL(txt)

    print("parsing result: ")
    print(ctx_elems)
    #print(data_elems)
    print(len(ctx_elems))
    print(len(data_elems))
