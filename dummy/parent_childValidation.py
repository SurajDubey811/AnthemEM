import hashlib
import xml.etree.ElementTree as ET
import re

import numpy as np
import pandas as pd
from functools import reduce
from operator import and_

pd.options.mode.chained_assignment = None


def get_calcSIT_xpath(ben_comp_path, namespace):
    xpath = '.'
    level = 1
    for ben_comp in ben_comp_path.split('>'):
        xpath += f"//{namespace}benefitComponent[@level='{level}'][@name='{ben_comp}']"
        level += 1
    xpath += f'/{namespace}calculationSituations/{namespace}calculationSituation'
    return xpath


def hase_node(comp_node):
    str_node = str(comp_node)
    result = hashlib.sha256(str_node.encode())
    return result.hexdigest()


def getNamespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def getNode(xmlfile, xpath):
    # create element tree object
    tree = ET.parse(xmlfile)
    # get root element
    root = tree.getroot()
    # return root
    # create empty list for news items
    newsitems = []
    namespace = getNamespace(root)
    # print(f'.//{namespace}planProperties')
    # xpath=".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='PainMgmt']//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='2'][@name='ArtificialDevice']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation"
    Elements = root.findall(xpath)
    # for elem in Elements:
    #     benefits=elem.findall(f'.//{namespace}calculationGroup//{namespace}calculation//{namespace}steps//{namespace}calculationStep//{namespace}benefitOption')
    #     for ele in benefits:
    #         ele.set('name','')
    #         ele.set('desc','')

    return Elements


def duplicate_identification_data(excel_file):
    excelData = pd.read_excel(excel_file)
    print(excelData.shape[0])
    # replacing null with ''
    excelData.fillna('', inplace=True)
    # changing index to 'id' field
    excelData.reset_index(level=0, inplace=True)
    excelData.rename({"index": "id"}, axis=1, inplace=True)
    group_by_cols = ["PATH_BEN_COMP_NAME", "BEN_COMP_LVL", "SIT_GRP_ID", "COIN",
                     "COIN_VAL",
                     "COIN_PERIOD",
                     "COIN_EOB",
                     "COIN_ACCUM",
                     "COIN_ACCUM_NET",
                     "COPAY",
                     "COPAY_VAL",
                     "COPAY_PERIOD",
                     "COPAY_EOB",
                     "COPAY_ACCUM",
                     "COPAY_ACCUM_NET",
                     "COPAY_MAX",
                     "COPAY_MAX_VAL",
                     "COPAY_MAX_PERIOD",
                     "COPAY_MAX_EOB",
                     "COPAY_MAX_ACCUM",
                     "COPAY_MAX_ACCUM_NET",
                     "DED",
                     "DED_VAL",
                     "DED_PERIOD",
                     "DED_EOB",
                     "DED_ACCUM",
                     "DED_ACCUM_NET",
                     "DED_AGG",
                     "DED_AGG_VAL",
                     "DED_AGG_PERIOD",
                     "DED_AGG_EOB",
                     "DED_AGG_ACCUM",
                     "DED_AGG_ACCUM_NET",
                     "DOL_LMT",
                     "DOL_LMT_VAL",
                     "DOL_LMT_PERIOD",
                     "DOL_LMT_EOB",
                     "DOL_LMT_ACCUM",
                     "DOL_LMT_ACCUM_NET",
                     "PENALTY",
                     "PENALTY_VAL",
                     "PENALTY_PERIOD",
                     "PENALTY_EOB",
                     "PENALTY_ACCUM",
                     "PENALTY_ACCUM_NET",
                     "SVC_DED",
                     "SVC_DED_VAL",
                     "SVC_DED_PERIOD",
                     "SVC_DED_EOB",
                     "SVC_DED_ACCUM",
                     "SVC_DED_ACCUM_NET",
                     "UNIT",
                     "UNIT_VAL",
                     "UNIT_PERIOD",
                     "UNIT_EOB",
                     "UNIT_ACCUM",
                     "UNIT_ACCUM_NET"]
    excelData['group_columns'] = excelData[group_by_cols].apply(
        lambda g: [str(i) for i in g.values.tolist() if str(i) != ''], axis=1)
    excelData['group_hash'] = excelData['group_columns'].apply(lambda g: hash("".join(g)))

    df = excelData[['id', 'BEN_COMP_NAME', 'BEN_COMP_LVL', 'PATH_BEN_COMP_NAME', 'CAL_TYPE_VAL', 'CAL_SIT_CHANGED',
                    'BEN_COMP_CHANGED', 'group_hash']]
    df.reset_index(level=0, inplace=True)
    df.rename({"index": "group_id"}, axis=1, inplace=True)
    df["parent_group_id"] = df['PATH_BEN_COMP_NAME'].apply(
        lambda g: df[df["PATH_BEN_COMP_NAME"] == ">".join(g.split(">")[:-1])]["group_id"].values.tolist())
    return df[["group_id", 'BEN_COMP_NAME', "PATH_BEN_COMP_NAME", "BEN_COMP_LVL", "parent_group_id", 'group_hash',
               'CAL_SIT_CHANGED']]


def contains(superset, subset) -> bool:
    # creates a list of boolean values and
    # combines them using the and operator
    return reduce(and_, [i in superset for i in subset])


def check_for_deletion(df, parent_path, comp_hash, deletion_dict):
    new_df = df[df["PATH_BEN_COMP_NAME"] == parent_path]
    parent_data = new_df.head(1)
    parent_hash_val = parent_data["LIST_HASH_VAL"].tolist()

    if contains(parent_hash_val, comp_hash):
        return True
    else:
        return False


def get_parent_id(path, path_id_dict):
    if path_id_dict[path]["parent_path"] != "":
        parent_id = path_id_dict[path_id_dict[path]["parent_path"]]["id"]
    else:
        parent_id = ""
    return parent_id


def get_parent_hashList(path, path_id_dict):
    parent_path = path_id_dict[path]["parent_path"]
    try:
        if parent_path != "":
            parent_hash_list = path_id_dict[parent_path]["hash_list"]
            return parent_hash_list
        else:
            return ""
    except KeyError:
        return ""


def main():
    xl_data = duplicate_identification_data('../SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx')
    xl_data = xl_data[xl_data['CAL_SIT_CHANGED'] != 'deletion']
    required_columns = ["BEN_COMP_NAME", "BEN_COMP_LVL", "PATH_BEN_COMP_NAME", "group_hash"]
    required_df = xl_data[required_columns].sort_values(by='BEN_COMP_LVL', ascending=False)
    paths = required_df["PATH_BEN_COMP_NAME"].unique().tolist()
    path_id_dict = dict()
    idx = 1
    for path in paths:
        temp_list = path.split(">")
        parent_path = ">".join(temp_list[0:-1])
        path_id_dict[path] = dict()
        path_id_dict[path]["id"] = idx
        if parent_path != "":
            path_id_dict[path]["parent_path"] = parent_path
        else:
            path_id_dict[path]["parent_path"] = ""
        idx += 1
    required_df['PATH_ID'] = required_df[['PATH_BEN_COMP_NAME']]. \
        apply(lambda a: path_id_dict[a["PATH_BEN_COMP_NAME"]]["id"], axis=1)
    required_df['PARENT_ID'] = required_df[['PATH_BEN_COMP_NAME']]. \
        apply(lambda a: get_parent_id(a["PATH_BEN_COMP_NAME"], path_id_dict), axis=1)

    required_columns.extend(["PATH_ID", "PARENT_ID"])
    required_df[required_columns].to_excel("hashcodes.xlsx")

    final_df = required_df.groupby(['PATH_ID', 'PARENT_ID', 'PATH_BEN_COMP_NAME', "BEN_COMP_LVL", "BEN_COMP_NAME"])[
        ["BEN_COMP_NAME", 'BEN_COMP_LVL', 'PATH_BEN_COMP_NAME', 'PATH_ID', 'PARENT_ID', 'group_hash']].apply(
        lambda g: g['group_hash'].tolist()).reset_index(name='LIST_HASH_VAL')

    for path in paths:
        path_id_dict[path]["hash_list"] = \
            final_df.loc[(final_df["PATH_ID"] == path_id_dict[path]["id"])]["LIST_HASH_VAL"].iloc[0]
    c = 0
    for item in path_id_dict.items():
        print(item)
        c += 1
    print(c)
    final_df["PARENT_HASH_LIST"] = final_df[["PATH_BEN_COMP_NAME"]]. \
        apply(lambda a: get_parent_hashList(a["PATH_BEN_COMP_NAME"], path_id_dict), axis=1)
    # final_df["PARENT_HASH_LIST"] = final_df[["PATH_ID", "PARENT_ID", "LIST_HASH_VAL", "PATH_BEN_COMP_NAME"]]. \
    #     apply(lambda a: get_parent_hashList(a["PATH_BEN_COMP_NAME"], a["PATH_ID"], a["PARENT_ID"], a["LIST_HASH_VAL"],
    #                                         path_id_dict), axis=1)

    final_df.to_excel("parent_child.xlsx")
    # deletion_dict = dict()
    #
    # # for i in range(len(final_df)):
    # #
    # #     comp_path = final_df["PATH_BEN_COMP_NAME"].iloc[i]
    # #     comp_level = final_df["BEN_COMP_LVL"].iloc[i]
    # #     comp_hash = final_df["LIST_HASH_VAL"].iloc[i]
    # #     temp_list = comp_path.split(">")
    # #     if int(comp_level) > 1:
    # #         parent_path = ">".join(temp_list[0:-1])
    # #         # print(parent_path)
    # #         # print(comp_path)
    # #         if check_for_deletion(final_df, parent_path, comp_hash, deletion_dict):
    # #             deletion_dict[str(final_df["PATH_BEN_COMP_NAME"].iloc[i])] = True
    # #             # print(True)
    # #         else:
    # #             deletion_dict[str(final_df["PATH_BEN_COMP_NAME"].iloc[i])] = False
    # #             # print(False)
    # #         # break
    # #     else:
    # #         deletion_dict[str(final_df["PATH_BEN_COMP_NAME"].iloc[i])] = False
    # #         # print(False)
    #
    # for k, v in deletion_dict.items():
    #     print(f"{k}: {v}")


if __name__ == '__main__':
    main()
