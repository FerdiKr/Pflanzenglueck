from dotmap import DotMap
import json
import os


class LocalizationRecursion:
    def __init__(self,dotmap,fallback_order):
        self.dotmap = dotmap
        self.fallback_order = fallback_order

    def __getattr__(self,attr):
        value = self.dotmap.get(attr)
        if type(value) == DotMap:
            for languagecode in self.fallback_order:
                if languagecode in value.keys():
                    return value[languagecode]
            return LocalizationRecursion(value,self.fallback_order)
        else:
            return value


class Localization:
    def __init__(self, languagecode, fallback_order=['en_US','de_DE'],additional_loc_files=[]):
        locfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),'localization.json')
        with open(locfilepath,'r',encoding='utf-8') as jsonfile:
            jsondict = json.load(jsonfile)
        self.localization_dict = jsondict
        for filepath in additional_loc_files:
            with open(filepath,'r',encoding='utf-8') as jsonfile:
                jsondict = json.load(jsonfile)
            self.localization_dict.update(jsondict)
        self.localization_dict = DotMap(self.localization_dict)

        self.languagecode = languagecode
        self.languagecode_escaped = 'c_'+self.languagecode

        self.fallback_order = fallback_order
        try:
            self.fallback_order.remove(languagecode)
        except ValueError:
            pass
        self.fallback_order = [languagecode]+self.fallback_order
        for languagecode in self.get_lowest_level_keys(self.localization_dict):
            if languagecode not in self.fallback_order:
                self.fallback_order.append(languagecode)
        self.fallback_order_escaped = ['c_'+langcode for langcode in self.fallback_order]

    @classmethod
    def get_lowest_level_keys(self,d):
        keys = set()
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    keys.update(self.get_lowest_level_keys(v))
                else:
                    keys.add(k)
        return keys

    def __getattr__(self,attr):
        iterator = LocalizationRecursion(self.localization_dict,self.fallback_order)
        value = iterator.__getattr__(attr)
        return value
    
# Testcode
def main():
    loc = Localization('de_DE')
    x = loc.anlagenauswahl.title
    print(x)
    print(type(x))

if __name__ == '__main__':
    main()
