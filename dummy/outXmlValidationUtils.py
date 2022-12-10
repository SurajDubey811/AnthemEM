import pandas as pd
import xml.etree.ElementTree as ET
import json
from utils.commonUtils import getNamespace, getBenComponentCalSITCount, get_calcSIT_xpath


class outPutxmlCheck:
    def __init__(self, excelFile, xmlfile):
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        self.root = tree.getroot()
        with open("config/unconditional_value_conf.json", "r") as f:
            self.validationDict = json.load(f)
        self.namespace = getNamespace(self.root)

        self.result_dict = {}
        self.diff_dict = {}
        self.same_keys = []

        required_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_TYPE_VAL', 'DX', 'DX_DESC', 'CAL_SAM_NAME',
                         'CAL_SIT_CHANGED', 'CAL_SIT_COMMENTS', 'BEN_COMP_CHANGED']
        self.excelData = pd.read_excel(excelFile)
        self.df = pd.DataFrame(self.excelData[required_cols])
        # changing index to 'id' field
        self.df.reset_index(level=0, inplace=True)
        self.df.rename({"index": "id"}, axis=1, inplace=True)

        # finding deleted components paths
        self.excelData.reset_index(level=0, inplace=True)
        self.excelData.rename({"index": "id"}, axis=1, inplace=True)
        df_index1 = self.excelData[self.excelData['BEN_COMP_CHANGED'] == 'deletion'].index
        df_index2 = self.excelData[self.excelData['CAL_SIT_CHANGED'] == 'deletion'].index
        del_indexes = list(dict.fromkeys(df_index1.tolist() + df_index2.tolist()).keys())
        del_paths = list(set(self.excelData['PATH_BEN_COMP_NAME'][self.excelData['id'].isin(del_indexes)].tolist()))
        self.df = pd.DataFrame(self.excelData[self.excelData['PATH_BEN_COMP_NAME'].isin(del_paths)])

        # removing deleted components
        self.df = self.df[self.df['BEN_COMP_CHANGED'] != 'deletion']
        self.df = self.df[self.df['CAL_SIT_CHANGED'] != 'deletion']

    def checkSameInOut(self, key, validDict):
        finalXpath = validDict[key]["xpath"].replace("namespace:", self.namespace)
        if key == "diagnosisCode":
            columns = ['DX', 'DX_DESC']
            group_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL']
            group_cols.extend(columns)
            grp_df = self.df.groupby(group_cols).size().reset_index(name='DX_COUNT')
            grp_df['xml_count'] = grp_df[['PATH_BEN_COMP_NAME', 'DX', 'DX_DESC']].apply(
                lambda a: len(self.root.findall(
                    f"{get_calcSIT_xpath(a['PATH_BEN_COMP_NAME'], self.namespace)}{finalXpath}[@id='{a['DX']}'][@desc='{a['DX_DESC']}']")),
                axis=1)
            grp_df['match'] = "No"
            grp_df.loc[grp_df['DX_COUNT'] == grp_df['DX_COUNT'], 'match'] = "Yes"
            grp_df.to_excel(f"output_files/outxml_{key}_check.xlsx", index=None)
            return grp_df["match"].tolist()

    def calSitExist_check(self):
        grp_df = self.df.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL'])['SIT_TYPE_VAL'].apply(
            lambda g: g.values.tolist()).reset_index(name='SIT_TYPE_VAL_LIST')
        grp_df['data'] = grp_df[['PATH_BEN_COMP_NAME', 'SIT_TYPE_VAL_LIST']].apply(
            lambda a: getBenComponentCalSITCount(a['PATH_BEN_COMP_NAME'], a['SIT_TYPE_VAL_LIST'], self.root), axis=1)
        grp_df[["countInXl", "countInXml", "founcInOpXml", "xpath"]] = pd.DataFrame(grp_df['data'].tolist(),
                                                                                    index=grp_df.index)
        grp_df.to_excel("output_files/outxml_calSitExist_check.xlsx", index=None)
        if "No" in grp_df["founcInOpXml"].tolist():
            self.diff_dict.update({"xlCalSITMatch": grp_df["founcInOpXml"].tolist()})
        self.result_dict.update({"xlCalSITMatch": "No" not in grp_df["founcInOpXml"].tolist()})

    def unconditionalValuesValidation(self):

        for key in self.validationDict:
            finalXpath = self.validationDict[key]["xpath"].replace("namespace:", self.namespace)
            statusList = []
            dataList = []
            prop_dict = dict()
            if self.validationDict[key]["expected_value"] != "same":
                items = self.root.findall(finalXpath)
                for item in items:
                    if "prop" in self.validationDict[key]:
                        # val = item.get(self.validationDict[key]["prop"])
                        val = item.attrib[self.validationDict[key]["prop"]]
                        if len(prop_dict) == 0:
                            prop_dict.update({key: [val]})
                        else:
                            prop_dict[key].append(val)
                    else:
                        val = item.text
                    if val is None:
                        val = ''
                    if self.validationDict[key]["expected_value"] != "same" or key != "specialtyCode":
                        statusList.append(val == self.validationDict[key]["expected_value"])
                        dataList.append(val)
            else:
                if key not in self.same_keys:
                    self.same_keys.append(key)
                    continue
            if len(statusList) > 0:
                self.result_dict.update({key: all(statusList)})
                if not all(statusList):
                    self.diff_dict.update({key: dataList})

    def checkValidations(self):
        self.unconditionalValuesValidation()
        self.calSitExist_check()
        for keys in self.same_keys:
            same_key_match_data = self.checkSameInOut(keys, self.validationDict)
            if "No" in same_key_match_data:
                self.diff_dict.update({keys: same_key_match_data})
            self.result_dict.update({keys: "No" not in same_key_match_data})

        if self.diff_dict:
            with open("output_files/unconditional_values_from_opXml.json", "w") as f:
                json.dump(self.diff_dict, f, indent=2)
        with open("output_files/outputXmlValidation.json", "w") as f:
            json.dump(self.result_dict, f, indent=2)
        return self.result_dict
