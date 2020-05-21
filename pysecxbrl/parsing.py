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

    def parseCalculationXML(self,text):
        utf8_parser = etree.XMLParser(encoding='utf-8')
        s = text.encode('utf-8')
        root = etree.fromstring(s, parser=utf8_parser)

        tree = self.getCalculationTree(root)

        return tree


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
            if divide is None:
                res[elemType] = elem[0].text
            else:
                res[elemType] = {}
                for item in divide:
                    # unitNumerator & unitDenominator for per share data are the only tags seen in this case
                    res[elemType][etree.QName(item).localname] = item[0].text

        if elemType == "context":
            entity = elem.find('.//{*}entity')
            if entity is not None:
                identif = entity.find('.//{*}identifier')
                res["scheme"] = identif.attrib["scheme"]
                res["identifier"] = identif.text

                seg = entity.find('.//{*}segment')
                if seg is not None:
                    res["segment"] = []
                    members = seg.findall('.//{*}explicitMember')
                    for member in members:
                        res["segment"].append({
                            "explicitMember":member.text,
                            "dimension":member.attrib["dimension"]
                        })

            period = elem.find('.//{*}period')
            if period is not None:
                instant = period.find('.//{*}instant')
                if instant is not None:
                    res["instant"] = instant.text

                start = period.find('.//{*}startDate')
                if start is not None:
                    res["startDate"] = start.text
                    res["endDate"] = period.find('.//{*}endDate').text

        return res

    def getCalculationTree(self, tree):
        roles = tree.findall(".//{*}roleRef")
        calc_links = tree.findall(".//{*}calculationLink")

        attrNs = tree.nsmap["xlink"]
        attribHref = "{{{}}}href".format(attrNs)
        attribLabel = "{{{}}}label".format(attrNs)
        attribFrom = "{{{}}}from".format(attrNs)
        attribTo = "{{{}}}to".format(attrNs)
        attribArcrole = "{{{}}}arcrole".format(attrNs)
        attribRole = "{{{}}}role".format(attrNs)

        res = {}

        for r in roles:
            id = r.attrib["roleURI"]
            name = r.attrib[attribHref]
            # doubling {{}} allows to escape the {} characters
            name = name.split("#")[1]

            res[id] = {"role":name}
            if self.copyIdInObj:
                res[id]["id"] = id

        for link in calc_links:
            if len(link) == 0:
                continue

            linkRole = link.attrib[attribRole]
            locs = link.findall(".//{*}loc")
            arcs = link.findall(".//{*}calculationArc")

            tags = {}
            for loc in locs:
                id = loc.attrib[attribLabel]
                name = loc.attrib[attribHref]
                name = name.split("#")[1]
                tags[id] = {"tag":name}

            for arc in arcs:
                t_from = arc.attrib[attribFrom]
                t_to = arc.attrib[attribTo]

                order = arc.attrib["order"]
                weight = arc.attrib["weight"]
                arcrole = arc.attrib[attribArcrole]

                if "calc" not in tags[t_from]:
                    tags[t_from]["calc"] = []
                tags[t_from]["calc"].append({"loc":t_to, "order":order,
                    "weight":weight,"arcrole":arcrole})

            res[linkRole]["tags"] = tags

        return res
