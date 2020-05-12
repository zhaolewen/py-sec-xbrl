import os

class XBRLExtractor:
    def __init__(self):
        pass

    def decompressPackage(self, path):
        pass

    def identifyFiles(self, folder):
        files = os.listdir(folder)

        res = {}
        for f in files:
            type = self.getFileType(folder, f)
            if type is not None:
                if type not in res:
                    res[type] = []

                res[type].append(f)

        return res

    def getFileType(self, folder, f_name):
        if f_name.endswith("_cal.xml"):
            return "calculation"
        if f_name.endswith("_def.xml"):
            return "definition"
        if f_name.endswith("_lab.xml"):
            return "label"
        if f_name.endswith("_pre.xml"):
            return "presentation"
        if f_name.endswith(".xsd"):
            return "xsd"

        lower = f_name.lower()
        if "exhibit" in lower:
            return "exhibit"
        if "certification" in lower:
            return "certification"
        if f_name.endswith("htm"):
            with open(os.path.join(folder, f_name)) as f:
                first_line = f.readline().lower()
                if "<!doctype html" in first_line:
                    return "html"
                if "<?xml" in first_line:
                    return "main"
        if f_name.endswith('.xml'):
            return "main"

        return None
