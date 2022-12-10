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
        with open("../config/unconditional_value_conf.json", "r") as f:
            self.validationDict = json.load(f)
        self.namespace = getNamespace(self.root)

        self.result_dict = {}
        self.diff_dict = {}
        self.same_keys = []

        required_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_TYPE_VAL', 'DX', 'DX_DESC', 'CAL_SAM_NAME', 'SPEC',
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
        self.df = self.df[required_cols]


outXMlCheck = outPutxmlCheck('SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx',
                             'SAM_ARTIFACTS/transformed_xml/31KT_Plan_Transformed.xml')
df = outXMlCheck.df
print(len(df))


for i in range(len(df)):
    print(df["SPEC"].iloc[i])

# for spec_data in df["SPEC"].astype(str):
#     print(spec_data)
