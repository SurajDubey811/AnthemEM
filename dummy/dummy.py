import xml.etree.ElementTree as et
import pandas as pd
import re
from lxml import etree as et
from utils.anthemUtils import getpath


def sub_namespace(node_data):
    namespace = "{http://wellpoint.com/schema/pushPlanRequest/v1}"
    node_data["Source Node"] = node_data["Source Node"].replace(namespace, "ns5:")
    node_data["Source Node"] = node_data["Source Node"].replace("/ns5:PushPlanData/", "")
    node_data["Source Node"] = re.sub("([\[\]])", "", node_data["Source Node"])
    node_data["Source Node"] = re.sub("(\d)+/+", "/", node_data["Source Node"])
    node_data["Source Node"] = re.sub("(\d)+$", "", node_data["Source Node"])
    return node_data


namespaces = {"ns5": "http://wellpoint.com/schema/pushPlanRequest/v1"}

# df = pd.read_excel("input/column_description.xlsx", sheet_name="Sheet1")

tree = et.parse("input/31KT_Plan.xml")
root = tree.getroot()

PlanID = root.find(".//ns5:planID", namespaces=namespaces).text
print(PlanID)
PLAN_PROXY_ID = root.find(".//ns5:planProxyID", namespaces=namespaces).text
print(PLAN_PROXY_ID)
# df1 = df[df["Updated by (Module)"] == "ingestion"]
# print(len(df1))
result_list = list()


rows_list = list()
for ele in root.findall(".//ns5:benefitComponent", namespaces=namespaces):



    row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": ele.get("level")}
    element_level = int(ele.get("level"))

    row_dict["PATH_BEN_COMP_NAME"], row_dict["PATH_BEN_COMP_DESC"] = getpath(ele)
    row_dict['SVC_DEF_ID'] = (ele.find(".//ns5:serviceDefinition", namespaces=namespaces)).get('id')
    row_dict['SVC_DEF_DESC'] = (ele.find(".//ns5:serviceDefinition", namespaces=namespaces)).get('desc')
    row_dict['SIT_TYPE_VAL'] = (ele.find(".//ns5:situationType", namespaces=namespaces)).get('value')

    if (ele.find(".//ns5:diagnosisCode", namespaces=namespaces)) is not None:
        row_dict["DX"] = (ele.find(".//ns5:diagnosisCode", namespaces=namespaces)).get('id')
        row_dict["DX_DESC"] = (ele.find(".//ns5:diagnosisCode", namespaces=namespaces)).get('desc')
    else:
        row_dict["DX"], row_dict["DX_DESC"] = None, None
    if (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)) is not None:
        row_dict['POS'] = (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get('id')
        row_dict['POS_DESC'] = (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get('desc')
    else:
        row_dict['POS'], row_dict["POS_DESC"] = None, None

    if (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)) is not None:
        row_dict['SPEC'] = (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get('id')
        row_dict['SPEC_DESC'] = (ele.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get('desc')
    else:
        row_dict['SPEC'], row_dict["SPEC_DESC"] = None, None

    if (ele.find(".//ns5:situationGroup", namespaces=namespaces)) is not None:
        row_dict['SIT_GRP_ID'] = (ele.find(".//ns5:situationGroup", namespaces=namespaces)).get('id')
        row_dict['SIT_GRP_DESC'] = (ele.find(".//ns5:situationGroup", namespaces=namespaces)).get('desc')
    else:
        row_dict['SIT_GRP_ID'], row_dict["SIT_GRP_DESC"] = None, None
    row_dict["CAL_TYPE_VAL"] = (ele.find(".//ns5:calculationType", namespaces=namespaces)).get('value')

    if (ele.find(".//ns5:examinerActionCode", namespaces=namespaces)) is not None:
        row_dict["EXAM_ACT_VAL"] = (ele.find(".//ns5:examinerActionCode", namespaces=namespaces)).get('value')
        row_dict["EXAM_ACT_DESC"] = (ele.find(".//ns5:examinerActionCode", namespaces=namespaces)).get('desc')
    else:
        row_dict["EXAM_ACT_VAL"] = None
        row_dict["EXAM_ACT_DESC"] = None
    steps = ele.find(".//ns5:steps", namespaces=namespaces)

    if (steps.findall(".//ns5:benefitOption", namespaces=namespaces)) is not None:
        for item in steps.findall(".//ns5:benefitOption", namespaces=namespaces):

            if item.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Coinsurance":
                row_dict["COIN"] = "Yes"
                row_dict["COIN_BO_NAME"] = item.get("name")
                row_dict["COIN_BO_DESC"] = item.get("desc")
                row_dict["COIN_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["COIN_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["COIN_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['COIN_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['COIN_ACCUM'] = None

                row_dict['COIN_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')

            if item.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Copayment":
                row_dict["COPAY"] = "Yes"
                row_dict["COPAY_BO_NAME"] = item.get("name")
                row_dict["COPAY_BO_DESC"] = item.get("desc")
                row_dict["COPAY_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["COPAY_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["COPAY_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['COPAY_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['COPAY_ACCUM'] = None

                row_dict['COPAY_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')
                row_dict['COPAY_MAX'] = None
                row_dict['COPAY_MAX_BO_NAME'] = None
                row_dict['COPAY_MAX_BO_DESC'] = None
                row_dict['COPAY_MAX_VAL'] = None
                row_dict['COPAY_MAX_PERIOD'] = None
                row_dict['COPAY_MAX_VAL'] = None
                row_dict['COPAY_MAX_EOB'] = None
                row_dict['COPAY_MAX_ACCUM'] = None
                row_dict['COPAY_MAX_ACCUM_NET'] = None

            if item.get("name") == "DedINNT1IndMed":
                row_dict["DED"] = "Yes"
                row_dict["DED_BO_NAME"] = item.get("name")
                row_dict["DED_BO_DESC"] = item.get("desc")
                row_dict["DED_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["DED_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["DED_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['DED_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['DED_ACCUM'] = None

                row_dict['DED_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')

            if item.get("name") == "DedINNT1FamMed":
                row_dict["DED_AGG"] = "Yes"
                row_dict["DED_AGG_BO_NAME"] = item.get("name")
                row_dict["DED_AGG_BO_DESC"] = item.get("desc")
                row_dict["DED_AGG_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["DED_AGG_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["DED_AGG_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['DED_AGG_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['DED_AGG_ACCUM'] = None

                row_dict['DED_AGG_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')

            if item.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "DollarLimit":
                row_dict["DOL_LMT"] = "Yes"
                row_dict["DOL_LMT_BO_NAME"] = item.get("name")
                row_dict["DOL_LMT_BO_DESC"] = item.get("desc")
                row_dict["DOL_LMT_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["DOL_LMT_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["DOL_LMT_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['DOL_LMT_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['DOL_LMT_ACCUM'] = None

                row_dict['DOL_LMT_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')

            if item.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Unit":
                row_dict["UNIT"] = "Yes"
                row_dict["UNIT_BO_NAME"] = item.get("name")
                row_dict["UNIT_BO_DESC"] = item.get("desc")
                row_dict["UNIT_VAL"] = float(item.find(".//ns5:benefitValue", namespaces=namespaces).text)
                row_dict["UNIT_PERIOD"] = item.find(".//ns5:benefitPeriod", namespaces=namespaces).get('value')
                row_dict["UNIT_EOB"] = int(item.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                if item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                    row_dict['UNIT_ACCUM'] = item.find(".//ns5:claimsAccumulatorName", namespaces=namespaces).get(
                        'value')
                else:
                    row_dict['UNIT_ACCUM'] = None

                row_dict['UNIT_ACCUM_NET'] = item.find(".//ns5:accumNetworkType", namespaces=namespaces).get('value')

    row_dict['PENALTY'] = None
    row_dict['PENALTY_BO_NAME'] = None
    row_dict['PENALTY_BO_DESC'] = None
    row_dict['PENALTY_VAL'] = None
    row_dict['PENALTY_PERIOD'] = None
    row_dict['PENALTY_EOB'] = None
    row_dict['PENALTY_ACCUM'] = None
    row_dict['PENALTY_ACCUM_NET'] = None
    row_dict['SVC_DED'] = None
    row_dict['SVC_BO_NAME'] = None
    row_dict['SVC_BO_DESC'] = None
    row_dict['SVC_DED_VAL'] = None
    row_dict['SVC_DED_PERIOD'] = None
    row_dict['SVC_DED_EOB'] = None
    row_dict['SVC_DED_ACCUM'] = None
    row_dict['SVC_DED_ACCUM_NET'] = None

    rows_list.append(row_dict)

df_result = pd.DataFrame(rows_list)
df_result.to_excel("xml_data.xlsx")

for item in rows_list:
    print(item)
print(len(rows_list))
