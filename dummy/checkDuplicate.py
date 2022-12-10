# Python code to illustrate parsing of XML files
# importing the required modules
import re
import xml.etree.ElementTree as ET

import pandas as pd
import json


def getNamespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def parseXML(xmlfile):
    # create element tree object
    tree = ET.parse(xmlfile)
    # get root element
    root = tree.getroot()
    # return root
    # create empty list for news items
    newsitems = []
    namespace = getNamespace(root)
    # print(f'.//{namespace}planProperties')
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}preAuth"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}autoAdjudicatedInd"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}visibility"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}keywords"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}specialtyCode/[@id]"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='UrgentCare']//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='2'][@name='UrgentCareProfessional']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation/{http://wellpoint.com/schema/pushPlanRequest/v1}visibility"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='UrgentCare']//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='2'][@name='UrgentCareProfessional']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation/{http://wellpoint.com/schema/pushPlanRequest/v1}situationDefinition/{http://wellpoint.com/schema/pushPlanRequest/v1}specialtyCode"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='UrgentCare']//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='2'][@name='UrgentCareProfessional']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation/../../{http://wellpoint.com/schema/pushPlanRequest/v1}keywords"
    # xpath=".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='UrgentCare']//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='2'][@name='UrgentCareProfessional']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation../../{http://wellpoint.com/schema/pushPlanRequest/v1}keywords"
    xpath = ".//{http://wellpoint.com/schema/pushPlanRequest/v1}benefitComponent[@level='1'][@name='Acupuncture']/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituations/{http://wellpoint.com/schema/pushPlanRequest/v1}calculationSituation/{http://wellpoint.com/schema/pushPlanRequest/v1}situationDefinition/{http://wellpoint.com/schema/pushPlanRequest/v1}diagnosisCodes/{http://wellpoint.com/schema/pushPlanRequest/v1}diagnosisCode"
    items = root.findall(xpath)
    print(items)
    xpath = "." + xpath.replace("ns5:", namespace)
    # print(xpath)
    # print(f".//{namespace}benefitComponent[@level='1']")
    # print(root.findall(f".//{namespace}benefitComponent[@level='1']"))
    item = root.findall(
        f".//{namespace}benefitComponent[@level='1'][@name='SurgSvcs']//{namespace}benefitComponent[@level='2'][@name='Facility']//{namespace}benefitComponent[@level='3'][@name='ReproductiveSurg']//{namespace}benefitComponent[@level='4'][@name='Abortion']")
    # print(item[0])
    # print(item[0].find(f'.//{namespace}situationType'))
    # iterate news items
    for item in root.findall(f".//{namespace}benefitComponent[@level='1']"):
        # print(item)
        # empty news dictionary
        news = {}

        # iterate child elements of item
        for child in item:
            pass
            # print(child)
            # # special checking for namespace object content:media
            # if child.tag == '{http://search.yahoo.com/mrss/}content':
            #     news['media'] = child.attrib['url']
            # else:
            #     news[child.tag] = child.text.encode('utf8')

        # append news dictionary to news items list
        newsitems.append(news)

    # return news items list
    return newsitems


def duplicate_identification_data_old(excel_file):
    excelData = pd.read_excel(excel_file)
    # print(excelData.shape[0])
    # replacing null with ''
    excelData.fillna('', inplace=True)
    # changing index to 'id' field
    excelData.reset_index(level=0, inplace=True)
    excelData.rename({"index": "id"}, axis=1, inplace=True)
    # excelData[["id","PATH_BEN_COMP_NAME","BEN_COMP_LVL",'DX', 'POS','SPEC',"CAL_SIT_CHANGED"]].to_excel("updation_rows.xlsx",index=None)
    # print(excelData.columns)
    # df = excelData.groupby('PATH_BEN_COMP_NAME')['id'].apply(list).reset_index(name='sibling_index_list')
    # df=excelData.groupby(['PATH_BEN_COMP_NAME','BEN_COMP_LVL'])[['id','DX', 'POS','SPEC']].apply(lambda g: g.values.tolist()).reset_index(name='sibling_index_list')
    #
    df = excelData.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL'])[['id', 'DX', 'POS', 'SPEC']].apply(
        lambda g: g.to_dict('records')).reset_index(name='sibling_index_list')
    df.reset_index(level=0, inplace=True)
    df.rename({"index": "group_id"}, axis=1, inplace=True)
    df["parent_group_id"] = df['PATH_BEN_COMP_NAME'].apply(
        lambda g: df[df["PATH_BEN_COMP_NAME"] == ">".join(g.split(">")[:-1])]["group_id"].values.tolist())
    # print(df[["group_id","PATH_BEN_COMP_NAME","BEN_COMP_LVL","parent_group_id","sibling_index_list"]])
    # print(excelData[['id','DX', 'POS','SPEC']].to_dict('records'))
    # print(df[df["PATH_BEN_COMP_NAME"]=="DurableMedEquip>LeaseRental>EarlyIntervention"]["sibling_index_list"])
    df[["group_id", "PATH_BEN_COMP_NAME", "BEN_COMP_LVL", "parent_group_id", "sibling_index_list"]].to_excel(
        "sibling_list.xlsx", index=None)


def get_calcSIT_xpath(ben_comp_path, namespace):
    xpath = '.'
    level = 1
    for ben_comp in ben_comp_path.split('>'):
        xpath += f"//{namespace}benefitComponent[@level='{level}'][@name='{ben_comp}']"
        level += 1
    xpath += f'/{namespace}calculationSituations/{namespace}calculationSituation'
    return xpath


def getBenComponentCalSITCount(ben_comp_path, sit_list, root):
    namespace = getNamespace(root)
    xpath = get_calcSIT_xpath(ben_comp_path, namespace)
    all(i != i for i in sit_list)
    if len(sit_list) == len(root.findall(xpath)):
        verdict = 'Yes'
    else:
        if all(i != i for i in sit_list):
            verdict = 'Yes'
        else:
            verdict = 'No'
    return len(sit_list), len(root.findall(xpath)), verdict, xpath


def getDiagonisCodeCount(ben_comp_path, sit_list, root):
    namespace = getNamespace(root)
    xpath = get_calcSIT_xpath(ben_comp_path, namespace)
    all(i != i for i in sit_list)
    if len(sit_list) == len(root.findall(xpath)):
        verdict = 'Yes'
    else:
        if all(i != i for i in sit_list):
            verdict = 'Yes'
        else:
            verdict = 'No'
    return len(sit_list), len(root.findall(xpath)), verdict, xpath


def calSitExist_check(df, root):
    grp_df = df.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL'])['SIT_TYPE_VAL'].apply(
        lambda g: g.values.tolist()).reset_index(name='SIT_TYPE_VAL_LIST')
    grp_df['data'] = grp_df[['PATH_BEN_COMP_NAME', 'SIT_TYPE_VAL_LIST']].apply(
        lambda a: getBenComponentCalSITCount(a['PATH_BEN_COMP_NAME'], a['SIT_TYPE_VAL_LIST'], root), axis=1)
    grp_df[["countInXl", "countInXml", "founcInOpXml", "xpath"]] = pd.DataFrame(grp_df['data'].tolist(),
                                                                                index=grp_df.index)
    grp_df.to_excel("output_files/outxml_calSitExist_check.xlsx", index=None)


def getXPATHTextPropValue(xpath, namespace, data, root):
    calSIT_xpath = get_calcSIT_xpath(xpath, namespace)
    finalXpath = calSIT_xpath + data['xpath'].replace("namespace:", namespace)
    print(finalXpath)
    items = root.findall(finalXpath)
    if len(items) != 1:
        return "Not FOund"
    if "prop" in data:
        return items[0].attrib[data["prop"]]
    else:
        return items[0].text


def checkSameInOut(key, validDict, df, root):
    namespace = getNamespace(root)
    finalXpath = validDict[key]["xpath"].replace("namespace:", namespace)
    if key == "diagnosisCode":
        columns = ['DX', 'DX_DESC']
        group_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL']
        group_cols.extend(columns)
        grp_df = df.groupby(group_cols).size().reset_index(name='DX_COUNT')
        grp_df['xml_count'] = grp_df[['PATH_BEN_COMP_NAME', 'DX', 'DX_DESC']].apply(
            lambda a: len(root.findall(
                f"{get_calcSIT_xpath(a['PATH_BEN_COMP_NAME'], namespace)}{finalXpath}[@id='{a['DX']}'][@desc='{a['DX_DESC']}']")),
            axis=1)
        grp_df['match'] = "No"
        grp_df.loc[grp_df['DX_COUNT'] == grp_df['DX_COUNT'], 'match'] = "Yes"
        grp_df.to_excel("output_files/outxml_dia_check.xlsx", index=None)
        return grp_df["match"].tolist()


def unconditionalValuesValidation(df, root):
    with open("../config/unconditional_value_conf.json", "r") as f:
        validationDict = json.load(f)

    namespace = getNamespace(root)
    result_dict = {}
    diff_dict = {}
    same_keys = []
    for key in validationDict:
        finalXpath = validationDict[key]["xpath"].replace("namespace:", namespace)
        statusList = []
        dataList = []
        if validationDict[key]["expected_value"] != "same":
            items = root.findall(finalXpath)
            for item in items:
                if "prop" in validationDict[key]:
                    val = item.attrib[validationDict[key]["prop"]]
                else:
                    val = item.text
                if val is None:
                    val = ''
                if validationDict[key]["expected_value"] != "same":
                    statusList.append(val == validationDict[key]["expected_value"])
                    dataList.append(val)
        else:
            if key not in same_keys:
                same_keys.append(key)
                continue
        if len(statusList) > 0:
            result_dict.update({key: all(statusList)})
            if all(statusList) == False:
                diff_dict.update({key: dataList})
    for keys in same_keys:
        same_key_match_data = checkSameInOut(keys, validationDict, df, root)
        if "No" in same_key_match_data:
            diff_dict.update({key: same_key_match_data})
        result_dict.update({key: "No" not in same_key_match_data})

    if diff_dict:
        with open("../output_files/unconditional_values_from_opXml.json", "w") as f:
            json.dump(diff_dict, f, indent=2)
    with open("output_files/unconditional_values_check.json", "w") as f:
        json.dump(result_dict, f, indent=2)
    return result_dict


def output_xml_validation(excelFile, xmlfile):
    excelData = pd.read_excel(excelFile)
    # changing index to 'id' field
    excelData.reset_index(level=0, inplace=True)
    excelData.rename({"index": "id"}, axis=1, inplace=True)

    # create element tree object
    tree = ET.parse(xmlfile)
    # get root element
    root = tree.getroot()
    required_cols = ['id', 'PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_TYPE_VAL', 'DX', 'DX_DESC', 'CAL_SAM_NAME',
                     'CAL_SIT_CHANGED', 'CAL_SIT_COMMENTS', 'BEN_COMP_CHANGED']
    df = excelData[required_cols]
    df = df[df['BEN_COMP_CHANGED'] != 'deletion']
    df = df[df['CAL_SIT_CHANGED'] != 'deletion']
    calSitExist_check(df, root)
    # print(unconditionalValuesValidation(df,root))


def get_group_id(item, id_list, isParent=False):
    if isParent:
        if ">" not in item:
            return -1
        else:
            parent_id = ">".join(item.split(">")[:-1])
            return list(dict.fromkeys(id_list)).index(parent_id)
    else:
        return list(dict.fromkeys(id_list)).index(item)


def checkProperties(prop, compTO, compWith, conf):
    returned_dict = dict()
    if compTO[prop] == compWith[prop]:
        returned_dict.update({compTO["id"]: ""})
        returned_dict.update({compWith["id"]: "deletion"})
        return returned_dict
    else:
        inConf1 = compTO[prop] in conf[prop]
        inConf2 = compWith[prop] in conf[prop]
        # print(prop,inConf1 , inConf2)
        # print(compTO)
        # print(compWith)
        if inConf1 and inConf2:
            # print("here")
            if conf[prop][compTO[prop]] > conf[prop][compTO[prop]]:
                returned_dict.update({compWith["id"]: "deletion"})
                returned_dict.update({compTO["id"]: "updated"})
            else:
                returned_dict.update({compTO["id"]: "deletion"})
                returned_dict.update({compWith["id"]: "updated"})
        elif inConf1 and not inConf2:
            if conf[prop][compTO[prop]] == 1:
                returned_dict.update({compWith["id"]: "deletion"})
                returned_dict.update({compTO["id"]: ""})
        elif not inConf1 and inConf2:
            if conf[prop][compWith[prop]] == 1:
                returned_dict.update({compTO["id"]: "deletion"})
                returned_dict.update({compWith["id"]: ""})
        else:
            returned_dict.update({compTO["id"]: ""})
    # print("returned_dict",returned_dict)
    return returned_dict


def delete_mark_1(colDict, conf, keys):
    h = lambda g: conf[keys][g] if g in conf[keys] else max(conf[keys].values()) + 1
    colValues = list(colDict.keys())
    minweight = min([h(i) for i in colValues])
    dd = dict()
    print(keys, colDict)

    for i in range(len(colValues) - 1):
        if h(colValues[i]) < h(colValues[i + 1]):
            if colValues[i] in ["", "ALL"]:
                colDict[colValues[i]][-1]['action'] = ''
            else:
                colDict[colValues[i]][-1]['action'] = 'updation'
            if colValues[i + 1] in conf[keys]:
                if colValues[i + 1] in ["", "ALL"]:
                    colDict[colValues[i + 1]][0]['action'] = 'deletion'
                else:
                    colDict[colValues[i + 1]][0]['action'] = 'update-delete'
            else:
                colDict[colValues[i + 1]][0]['action'] = 'deletion'
            colDict[colValues[i + 1]][0]['action'] = 'deletion'
        elif h(colValues[i]) > h(colValues[i + 1]):
            if colValues[i + 1] in ["", "ALL"]:
                colDict[colValues[i + 1]][0]['action'] = ''
            else:
                colDict[colValues[i + 1]][0]['action'] = 'updation'
            if colValues[i] in conf[keys]:
                if colValues[i] in ["", "ALL"]:
                    colDict[colValues[i]][-1]['action'] = 'deletion'
                else:
                    colDict[colValues[i]][-1]['action'] = 'update-delete'
            else:
                colDict[colValues[i]][-1]['action'] = 'deletion'
        elif h(colValues[i]) == h(colValues[i + 1]):
            if i == 0:
                if colValues[i] == colValues[i + 1]:
                    if h(colValues[i]) == minweight:
                        colDict[colValues[i]][-1]['action'] = ''
                        colDict[colValues[i + 1]][0]['action'] = 'deletion'
                    else:
                        colDict[colValues[i]][-1]['action'] = 'deletion'
                        colDict[colValues[i + 1]][0]['action'] = 'deletion'
                else:
                    if h(colValues[i]) > minweight:
                        colDict[colValues[i]][-1]['action'] = 'deletion'
                        colDict[colValues[i + 1]][0]['action'] = 'deletion'
                    else:
                        colDict[colValues[i]][-1]['action'] = ''
                        colDict[colValues[i + 1]][0]['action'] = ''
                    # if colValues[i] in conf[keys] and colValues[i+1] in conf[keys]:
                    #     colDict[colValues[i]][-1]['action']=''
                    #     colDict[colValues[i + 1]][0]['action'] = 'deletion'
                    # else:
                    #     colDict[colValues[i]][-1]['action'] = 'deletion'
                    #     colDict[colValues[i + 1]][0]['action'] = 'deletion'

            else:
                colDict[colValues[i + 1]][0]['action'] = colDict[colValues[i]][-1]['action']
        for t in colDict[colValues[i]]:
            dd.update({t['id']: t["action"]})
        for t in colDict[colValues[i + 1]]:
            dd.update({t['id']: t["action"]})
    return dd


def delete_mark(colDict, conf, keys):
    h = lambda g: conf[keys][g] if g in conf[keys] else max(conf[keys].values()) + 1
    colValues = list(colDict.keys())
    minweight = min([h(i) for i in colValues])
    dd = dict()
    # print(keys,colDict)
    tempDD = dict()
    for key, val in colDict.items():
        for i in val:
            tempDD.update({i["id"]: {'val': key, 'action': i['action']}})
    colDataInDict = dict()
    tempDDSortedKeys = sorted(tempDD.keys())
    for key in tempDDSortedKeys:
        colDataInDict.update({key: tempDD[key]})
    # print(tempDDSortedKeys)
    # print(colValues)
    for i in range(len(tempDDSortedKeys) - 1):
        if h(colDataInDict[tempDDSortedKeys[i]]['val']) < h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
            # if already generalized
            if colDataInDict[tempDDSortedKeys[i]]['val'] in ['', 'ALL']:
                colDataInDict[tempDDSortedKeys[i]]['action'] = ''
            else:
                # if not generalized
                colDataInDict[tempDDSortedKeys[i]]['action'] = 'updation'
            if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in conf[keys]:
                if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in ["", "ALL"]:
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                else:
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'update-delete'
            else:
                colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
        elif h(colDataInDict[tempDDSortedKeys[i]]['val']) > h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
            # if already generalized

            if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in ['', 'ALL']:
                colDataInDict[tempDDSortedKeys[i + 1]]['action'] = ''
                # print(list(range(0,i-1))[::-1],i-1)
                for j in list(range(0, i - 1))[::-1]:
                    if h(colDataInDict[tempDDSortedKeys[j]]['val']) == h(colDataInDict[tempDDSortedKeys[i]]['val']):
                        colDataInDict[tempDDSortedKeys[j]]['action'] = 'deletion'
                    else:
                        break
            else:
                # if not generalized
                if colDataInDict[tempDDSortedKeys[i]]['val'] in conf[keys]:
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'updation'
            if colDataInDict[tempDDSortedKeys[i]]['val'] in conf[keys]:
                if colDataInDict[tempDDSortedKeys[i]]['val'] in ["", "ALL"]:
                    colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
                else:
                    colDataInDict[tempDDSortedKeys[i]]['action'] = 'update-delete'
            else:
                colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
        elif h(colDataInDict[tempDDSortedKeys[i]]['val']) == h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
            if i == 0:
                if colDataInDict[tempDDSortedKeys[i]]['val'] == colDataInDict[tempDDSortedKeys[i + 1]]['val']:
                    colDataInDict[tempDDSortedKeys[i]]['action'] = ''
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                else:
                    if h(colDataInDict[tempDDSortedKeys[i]]['val']) > minweight:
                        colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                    else:
                        colDataInDict[tempDDSortedKeys[i]]['action'] = ''
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = ''

            else:
                if colDataInDict[tempDDSortedKeys[i]]['val'] not in ['', 'ALL']:
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = colDataInDict[tempDDSortedKeys[i]]['action']

    for i in colDataInDict:
        dd.update({i: colDataInDict[i]['action']})
    return dd


def checkDuplicateCalSit(listProps):
    conf = {"DX": {"ALL": 1, "": 1}, "POS": {"": 1, "ALL": 1}, "SPEC": {'ALL': 1, "PCP": 2, "SPC": 3}}
    returned_dict = {}
    df = pd.DataFrame(listProps)
    new_cols = ["id"]
    for keys in conf:
        df[f'{keys}_mark'] = df[keys].apply(
            lambda g: conf[keys][g] if g in conf[keys] else max(conf[keys].values()) + 1)
        new_cols.extend([f'{keys}', f'{keys}_mark'])
    # df["dx_del"]=df[['id','DX']].apply(lambda g: delete_mark(g.to_dict('records'),conf,'DX'),axis=1)
    dx_df = df.groupby(['DX'], sort=False)[['id']].apply(
        lambda g: [dict(i, **{"action": ""}) if g.to_dict('records')[0] == i else dict(i, **{"action": "deletion"}) for
                   i in g.to_dict('records')]).reset_index(name='index_list')
    pos_df = df.groupby(['POS'], sort=False)[['id']].apply(
        lambda g: [dict(i, **{"action": ""}) if g.to_dict('records')[0] == i else dict(i, **{"action": "deletion"}) for
                   i in g.to_dict('records')]).reset_index(name='index_list')
    spec_df = df.groupby(['SPEC'], sort=False)[['id']].apply(
        lambda g: [dict(i, **{"action": ""}) if g.to_dict('records')[0] == i else dict(i, **{"action": "deletion"}) for
                   i in g.to_dict('records')]).reset_index(name='index_list')
    # print(dx_df)
    # print(pos_df)
    # print(spec_df)
    # print(dx_df.set_index('DX').to_dict()['index_list'])
    propColDupData = {}
    # if only two or more group exist then need to consider this creteria
    if dx_df.shape[0] > 1:
        # need to consider the creteria only if some spectlized
        # value exist in group which might be deleted
        if sorted(dx_df['DX'].tolist()) != ['', 'ALL']:
            data = delete_mark(dx_df.set_index('DX').to_dict()['index_list'], conf, 'DX')
            propColDupData.update({"DX": data})
    # if only two or more group exist then need to consider this creteria
    if pos_df.shape[0] > 1:
        # need to consider the creteria only if some spectlized
        # value exist in group which might be deleted
        if sorted(pos_df['POS'].tolist()) != ['', 'ALL']:
            data = delete_mark(pos_df.set_index('POS').to_dict()['index_list'], conf, 'POS')
            propColDupData.update({"POS": data})
    # if only two or more group exist then need to consider this creteria
    if spec_df.shape[0] > 1:
        data = delete_mark(spec_df.set_index('SPEC').to_dict()['index_list'], conf, 'SPEC')
        propColDupData.update({"SPEC": data})
        # print('SPEC',data)
    # print(propColDupData)
    identifiedProps = list(propColDupData.keys())
    finalVerdict = []
    if len(identifiedProps) > 0:
        for keys in propColDupData[identifiedProps[0]].keys():
            delete_count = 0
            row_del_stat = []
            for i in identifiedProps:
                # print(keys, propColDupData[i][keys], i)
                if propColDupData[i][keys] in ['deletion', 'update-delete']:
                    delete_count += 1
                row_del_stat.append(propColDupData[i][keys])
            # print(delete_count)
            if delete_count == len(identifiedProps):
                finalVerdict.append({"id": keys, "CAL_SIT_CHANGED": "deletion"})
            else:
                if "updation" in row_del_stat:
                    if "deletion" not in row_del_stat:
                        finalVerdict.append({"id": keys, "CAL_SIT_CHANGED": "updation"})
                    else:
                        finalVerdict.append({"id": keys, "CAL_SIT_CHANGED": "deletion"})
                else:
                    finalVerdict.append({"id": keys, "CAL_SIT_CHANGED": ""})
    if len(finalVerdict) == 0:
        return [{'id': i['id'], "CAL_SIT_CHANGED": ""} for i in listProps]
    else:
        return finalVerdict

    # print(df[['id','DX', 'DX_mark','dx_del']])
    # for i in range(len(listProps)):
    #     for j in range(i+1,len(listProps)):
    #         print("compareTO", listProps[i])
    #         print("compareWith", listProps[j])
    #         dxDict = checkProperties("DX", listProps[i], listProps[j], conf)
    #         print("dxDict", dxDict)
    #         pos_dict = checkProperties("POS", listProps[i], listProps[j], conf)
    #         print("pos_dict", pos_dict)
    #         spec_dict = checkProperties("SPEC", listProps[i], listProps[j], conf)
    #         # print("dxDict",dxDict)
    #         # print("pos_dict",pos_dict)
    #         print("spec_dict", spec_dict)
    #         print("*" * 20)
    #         returned_dict.update(dxDict)
    #         returned_dict.update(pos_dict)
    #         returned_dict.update(spec_dict)
    #         if i!=j:
    #             pass
    # if listProps[i]["DX"]==listProps[j]["DX"]:
    #     if listProps[i]["POS"]==listProps[j]["POS"]:
    #         if listProps[i]["SPEC"] == listProps[j]["SPEC"]:
    #             returned_dict.update({listProps[i]["id"]: ""})
    #         else:
    #             returned_dict.update(checkProperties("SPEC",listProps[i],listProps[j],conf))
    #     else:
    #         returned_dict.update(checkProperties("POS", listProps[i], listProps[j], conf))
    # else:
    #     returned_dict.update(checkProperties("DX", listProps[i], listProps[j], conf))
    # print(returned_dict)


def duplicate_identification_data(excel_file):
    excelData = pd.read_excel(excel_file)
    # print(excelData.shape[0])
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

    df1 = excelData.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_GRP_ID', 'group_hash'])[
        ['id', 'DX', 'POS', 'SPEC', 'SIT_TYPE_DESC']].apply(lambda g: g.to_dict('records')).reset_index(
        name='sibling_index_list')
    df2 = excelData.groupby(['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_GRP_ID', 'group_hash'])[
        ['id', 'CAL_SIT_CHANGED']].apply(lambda g: g.to_dict('records')).reset_index(name='change_sit_list')
    df = pd.merge(df1, df2, on=['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_GRP_ID', 'group_hash'])
    df['qa_verdict_on_changed_sit'] = df['sibling_index_list'].apply(lambda g: checkDuplicateCalSit(g))
    df['qa_verdict_match'] = df[['change_sit_list', 'qa_verdict_on_changed_sit']].apply(
        lambda a: "Yes" if a['change_sit_list'] == a['qa_verdict_on_changed_sit'] else "No", axis=1)
    df3 = pd.DataFrame([j for i in df['qa_verdict_on_changed_sit'].tolist() for j in i])
    df3.columns = ['id', 'EXP_CAL_SIT_CHANGED']
    print(df3.columns)
    df4 = pd.merge(excelData, df3, on='id')
    print(df4.columns)
    mismatched_indexs = [j['id'] for i in df[df['qa_verdict_match'] == "No"]['qa_verdict_on_changed_sit'].tolist() for j
                         in i]
    # df.reset_index(level=0, inplace=True)
    # df.rename({"index": "group_id"}, axis=1, inplace=True)
    df['BEN_COMP_NAME_ID'] = df['PATH_BEN_COMP_NAME'].apply(
        lambda g: get_group_id(g, df['PATH_BEN_COMP_NAME'].values.tolist()))
    df['parent_group_id'] = df['PATH_BEN_COMP_NAME'].apply(
        lambda g: get_group_id(g, df['PATH_BEN_COMP_NAME'].values.tolist(), isParent=True))

    # df["parent_group_id"]=df['PATH_BEN_COMP_NAME'].apply(lambda g: df[df["PATH_BEN_COMP_NAME"]==">".join(g.split(">")[:-1])]["group_id"].values.tolist())
    with pd.ExcelWriter("sibling_list.xlsx", engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="comparision")
        excelData[
            ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_GRP_ID', 'DX', 'POS', 'SPEC', 'group_hash', 'CAL_SIT_CHANGED',
             'SIT_TYPE_DESC']].to_excel(writer, sheet_name="details")
        if len(mismatched_indexs) > 0:
            df4[df4.index.isin(mismatched_indexs)][
                ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_GRP_ID', 'DX', 'POS', 'SPEC', 'group_hash',
                 'CAL_SIT_CHANGED', 'EXP_CAL_SIT_CHANGED', 'SIT_TYPE_DESC']].to_excel(writer,
                                                                                      sheet_name="mismatch_Data")


def identify_sibling_duplicate(excelFile, xmlFile):
    required_cols = ['PATH_BEN_COMP_NAME', 'BEN_COMP_LVL', 'SIT_TYPE_VAL', 'DX',
                     'POS', 'SPEC', 'SIT_GRP_ID', 'SIT_TYPE_DESC',
                     'CAL_SIT_CHANGED', 'CAL_SIT_COMMENTS', 'BEN_COMP_CHANGED']
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
    excelData = pd.read_excel(excelFile)
    # df = pd.DataFrame(excelData[required_cols])
    # changing index to 'id' field
    excelData.reset_index(level=0, inplace=True)
    excelData.rename({"index": "id"}, axis=1, inplace=True)
    df_index1 = excelData[excelData['BEN_COMP_CHANGED'] == 'deletion'].index
    df_index2 = excelData[excelData['CAL_SIT_CHANGED'] == 'deletion'].index
    print(len(df_index1.tolist()))
    print(len(df_index2.tolist()))
    del_indexes = list(dict.fromkeys(df_index1.tolist() + df_index2.tolist()).keys())
    del_paths = list(set(excelData['PATH_BEN_COMP_NAME'][excelData['id'].isin(del_indexes)].tolist()))
    df1 = pd.DataFrame(excelData[excelData['PATH_BEN_COMP_NAME'].isin(del_paths)])

    df1['group_columns'] = df1[group_by_cols].apply(
        lambda g: [str(i) for i in g.values.tolist() if str(i) != ''], axis=1)
    df1['group_hash'] = df1['group_columns'].apply(lambda g: hash("".join(g)))
    required_cols.append("group_hash")
    # df2 = df1[(df1['BEN_COMP_CHANGED'] == 'deletion') | (df1['CAL_SIT_CHANGED'] == 'deletion')]
    # df2 = df2[required_cols]
    # print(len(df2))
    df1 = df1[(df1['BEN_COMP_CHANGED'] != 'deletion') & (df1['CAL_SIT_CHANGED'] != 'deletion')]
    df1 = df1[required_cols]

    df2 = df1[df1["SPEC"] != 'ALL']

    df2[required_cols].to_excel("deleted_rows.xlsx")


def main():
    # load rss from web to update existing xml file
    prop_list = [{'id': 100, 'DX': 'RTNDX', 'POS': '', 'SPEC': 'ALL'},
                 {'id': 101, 'DX': 'ALL', 'POS': '', 'SPEC': 'ALL'},
                 {'id': 102, 'DX': 'RTNDX', 'POS': '', 'SPEC': 'ALL'},
                 {'id': 103, 'DX': 'ALL', 'POS': '', 'SPEC': 'ALL'}]
    duplicate_identification_data('../SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx')
    # identify_sibling_duplicate('SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx')


if __name__ == "__main__":
    # calling main function
    main()
