from lxml import etree
import re


class SECParser:
    def __init__(self):
        self.copyIdInObj = False

    def parseMainXBRL(self, text):
        utf8_parser = etree.XMLParser(encoding='utf-8')
        s = text.encode('utf-8')
        root = etree.fromstring(s, parser=utf8_parser)

        #main_elems = root.findall(".//dei:DocumentType",namespaces=root.nsmap)
        # print(len(main_elems))
        data_elems = self.getDataElementsAsDict(root)
        ctx_elems = self.getContextElementsAsDict(root)


        return ctx_elems, data_elems

    def getDataElementsAsDict(self, tree):
        data_elems = tree.findall(".//*[@contextRef]")

        res = {}
        for elem in data_elems:
            item = {
                "tag":etree.QName(elem).localname,
                "value":elem.text,
                "prefix":elem.prefix
            }
            for attr in elem.attrib:
                item[attr] = elem.attrib[attr]

            res[elem.attrib["id"]] = item

        return res

    def getContextElementsAsDict(self, tree):
        ctx_elems = tree.findall(".//xbrli:*[@id]",namespaces=tree.nsmap)

        res = {}
        for elem in ctx_elems:
            res[elem.attrib["id"]] = self.formatContextElement(elem)

        return res

    def formatContextElement(self, elem):
        res = {}
        if self.copyIdInObj:
            item["id"] = res.attrib["id"]

        elemType = etree.QName(elem).localname
        res["type"] = elemType

        if elemType == "unit":
            divide = elem.find('.//{*}divide')
            if not divide:
                res[elemType] = elem[0].text
            else:
                res[elemType] = {}
                for item in divide:
                    # unitNumerator & unitDenominator for per share data are the only tags seen in this case
                    res[elemType][etree.QName(item).localname] = item[0].text

        if elemType == "context":
            entity = elem.find('.//{*}entity')
            if entity:
                identif = entity.find('.//{*}identifier')
                res["scheme"] = identif.attrib["scheme"]
                res["identifier"] = identif.text
                seg = entity.find('.//{*}segment')
                if seg:
                    res["segment"] = []
                    members = seg.findall('.//{*}explicitMember')
                    for member in members:
                        res["segment"].append({
                            "explicitMember":member.text,
                            "dimension":member.attrib["dimension"]
                        })

            period = elem.find('.//{*}period')
            if period:
                instant = period.find('.//{*}instant')
                if instant:
                    res["instant"] = instant.text
                start = period.find('.//{*}startDate')
                if start:
                    res["startDate"] = start.text
                    res["endDate"] = period.find('.//{*}endDate').text

        return res
