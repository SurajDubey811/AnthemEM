import pandas as pd
import xml.etree.ElementTree as ET
import json
from utils.commonUtils import getNamespace,getBenComponentCalSITCount,get_calcSIT_xpath,getExpUpdatePropCount

class outPutxmlCheck:
    def __init__(self,excelFile,xmlfile):
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        self.root = tree.getroot()
        with open("config/unconditional_value_conf.json", "r") as f:
            self.validationDict =json.load(f)
        self.namespace = getNamespace(self.root)

        self.result_dict = {}
        self.diff_dict = {}
        self.same_keys = []

        required_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_TYPE_VAL','DX', 'DX_DESC', 'SPEC','SPEC_DESC','CAL_SAM_NAME',
                         'CAL_SIT_CHANGED', 'CAL_SIT_COMMENTS', 'BEN_COMP_CHANGED']
        self.excelData = pd.read_excel(excelFile)
        self.req_df = pd.DataFrame(self.excelData[required_cols])
        # changing index to 'id' field
        self.req_df.reset_index(level=0, inplace=True)
        self.req_df.rename({"index": "id"}, axis=1, inplace=True)


    def checkSameInOut(self,key, validDict):
        finalXpath = validDict[key]["xpath"].replace("namespace:", self.namespace)
        if key == "diagnosisCode":
            columns = ['DX', 'DX_DESC']
            group_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL']
            group_cols.extend(columns)
            grp_df = self.req_df.groupby(group_cols).size().reset_index(name='DX_COUNT')
            grp_df['xml_count'] = grp_df[['PATH_BEN_COMP_NAME', 'DX', 'DX_DESC']].apply(
                lambda a: len(self.root.findall(
                    f"{get_calcSIT_xpath(a['PATH_BEN_COMP_NAME'], self.namespace)}{finalXpath}[@id='{a['DX']}'][@desc='{a['DX_DESC']}']")),
                axis=1)
            grp_df['match'] = "No"
            grp_df.loc[grp_df['DX_COUNT'] == grp_df['DX_COUNT'], 'match'] = "Yes"
            grp_df.to_excel(f"output_files/outxml_{key}_check.xlsx", index=None)
            return grp_df["match"].tolist()
        elif key == "specialtyCode":
            df_up_index = self.req_df[self.req_df['CAL_SIT_CHANGED'] == 'updation'].index
            update_paths = list(set(self.req_df['PATH_BEN_COMP_NAME'][self.req_df['id'].isin(df_up_index)].tolist()))
            df = pd.DataFrame(self.req_df[self.req_df['PATH_BEN_COMP_NAME'].isin(update_paths)])
            df1 = df.groupby(["PATH_BEN_COMP_NAME",
                              "BEN_COMP_LVL"])[['id', 'SPEC', 'SPEC_DESC', 'CAL_SIT_CHANGED', 'BEN_COMP_CHANGED'
                                                ]].apply(lambda g: g.to_dict('records')).reset_index(
                name='updated_id_grp')
            match_cols=[]
            for i in range(len(validDict[key]["prop"])):
                df1[f"expected_all_count_{validDict[key]['prop'][i]}"] = df1["updated_id_grp"].apply(lambda g:getExpUpdatePropCount(g,validDict[key]["xl_col"][i],validDict[key]["expected_value"][i]))
                df1[f"op_all_spec_count_{validDict[key]['prop'][i]}"] = df1["PATH_BEN_COMP_NAME"].apply(
                    lambda g: [item.attrib[validDict[key]["prop"][i]]==validDict[key]["expected_value"][i]
                               for item in self.root.findall(f"{get_calcSIT_xpath(g, self.namespace)}{finalXpath}")].count(True))
                df1[f"spec_code_updation_done_{validDict[key]['prop'][i]}"] = df1[[f"op_all_spec_count_{validDict[key]['prop'][i]}", f"expected_all_count_{validDict[key]['prop'][i]}"]] \
                    .apply(lambda g: "Yes" if g[f"op_all_spec_count_{validDict[key]['prop'][i]}"] == g[f"expected_all_count_{validDict[key]['prop'][i]}"]
                else "No", axis=1)
                match_cols.append(f"spec_code_updation_done_{validDict[key]['prop'][i]}")
            df1["final_prop_match"]=df1[match_cols].apply(lambda g: "Yes" if len(g.tolist())==g.tolist().count("Yes") else "No",axis=1)

            with pd.ExcelWriter(f"output_files/outxml_{key}_check.xlsx", engine='openpyxl') as writer:
                df1.sort_values(by=["PATH_BEN_COMP_NAME",
                                    "BEN_COMP_LVL"], ascending=False).to_excel(writer, sheet_name="compare")
                df.sort_values(by=["PATH_BEN_COMP_NAME",
                                         "BEN_COMP_LVL"], ascending=False).to_excel(writer, sheet_name="details")
            return df1["final_prop_match"].tolist()
    def extractionValidation(self):
        # removing deleted components
        df = self.req_df[self.req_df['BEN_COMP_CHANGED'] != 'deletion']
        df = df[df['CAL_SIT_CHANGED'] != 'deletion']
        grp_df = df.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL'])['SIT_TYPE_VAL'].apply(
            lambda g: g.values.tolist()).reset_index(name='SIT_TYPE_VAL_LIST')
        grp_df['data'] = grp_df[['PATH_BEN_COMP_NAME', 'SIT_TYPE_VAL_LIST']].apply(
            lambda a: getBenComponentCalSITCount(a['PATH_BEN_COMP_NAME'], a['SIT_TYPE_VAL_LIST'], self.root), axis=1)
        grp_df[["countInXl", "countInXml", "founcInOpXml", "xpath"]] = pd.DataFrame(grp_df['data'].tolist(),
                                                                                    index=grp_df.index)
        grp_df.to_excel("output_files/outxml_calSitExist_check.xlsx", index=None)
        if "No" in grp_df["founcInOpXml"].tolist():
            self.diff_dict.update({"xlCalSITMatch": grp_df["founcInOpXml"].tolist()})
        self.result_dict.update({"xlCalSITMatch": "No" not in grp_df["founcInOpXml"].tolist()})

    def normalization_validation(self):
        for key in self.validationDict:
            finalXpath=self.validationDict[key]["xpath"].replace("namespace:",self.namespace)
            statusList=[]
            dataList=[]
            if self.validationDict[key]["pipeline_stage"] == "normalization":
                items = self.root.findall(finalXpath)
                for item in items:
                    if "prop" in self.validationDict[key]:
                        val= item.attrib[self.validationDict[key]["prop"]]
                    else:
                        val=item.text
                    if val is None:
                        val=''
                    statusList.append(val==self.validationDict[key]["expected_value"])
                    dataList.append(val)
            else:
                if key not in self.same_keys:
                    self.same_keys.append(key)
                    continue
            if len(statusList)>0:
                self.result_dict.update({key:all(statusList)})
                if all(statusList)==False:
                    self.diff_dict.update({key:dataList})

    def checkValidations(self):
        self.normalization_validation()
        self.extractionValidation()
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


