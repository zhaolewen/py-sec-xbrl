from lxml import etree
import re


class SECParser:
    def __init__(self):
        pass

    def parseMainXBRL(self, text):
        utf8_parser = etree.XMLParser(encoding='utf-8')
        s = text.encode('utf-8')
        root = etree.fromstring(s, parser=utf8_parser)

        main_elems = root.findall(".//dei:DocumentType",namespaces=root.nsmap)
        ctx_elems = root.findall(".//*[@id]")
        data_elems = root.findall(".//*[@contextRef]")

        print(len(main_elems))
        print(len(ctx_elems))
        print(len(data_elems))

        res = {}
        for elem in data_elems:
            res[elem.attrib["id"]] = {etree.QName(elem).localname:elem.text}

        return res
