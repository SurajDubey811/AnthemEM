import numpy as np
import pandas as pd
from lxml import etree as et
from utils.anthemUtils import getpath, get_element_level
import re

# def get_element_level(element):
#     while "benefitComponent" not in element.tag:
#         element = element.getparent()
#     return element.get('level')



def getNamespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


tree = et.parse("SAM_ARTIFACTS/input_xml/31KT_Plan.xml")
excel_df = pd.read_excel("SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx")
root = tree.getroot()

# namespaces = {"ns5": "http://wellpoint.com/schema/pushPlanRequest/v1"}
namespace = getNamespace(root)
print(namespace)

PlanID = root.find(f".//{namespace}planID").text
print(PlanID)
PLAN_PROXY_ID = root.find(f".//{namespace}planProxyID").text
print(PLAN_PROXY_ID)
summ = sum1 = calc_sits = ben_comps = ben_compx = 0
rows_list = list()

for ele in root.findall(f".//{namespace}benefitComponent"):
    ben_comp_level = ele.get("level")
    ben_comps += 1
    flagx = True
    if len(ele.findall(f".//{namespace}calculationSituation")) > 0:
        for calc_sit in ele.findall(f".//{namespace}calculationSituation"):
            row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                        "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": ele.get("level"),
                        "PATH_BEN_COMP_NAME": (getpath(ele))[0], "PATH_BEN_COMP_DESC": (getpath(ele))[1],
                        'SVC_DEF_ID': ele.find(f".//{namespace}serviceDefinition").get('id'),
                        'SVC_DEF_DESC': ele.find(f".//{namespace}serviceDefinition").get('desc')}
            # row_dict["BEN_COMP_SAM_NAME"] = row_dict["SVC_DEF_ID"]
            calc_sit_level = get_element_level(calc_sit)
            if calc_sit_level == ben_comp_level:
                flagx = False
                row_dict['SIT_TYPE_VAL'] = calc_sit.find(f".//{namespace}situationType").get(
                    'value')
                row_dict['SIT_TYPE_DESC'] = calc_sit.find(f".//{namespace}situationType").get(
                    'desc')
                # row_dict["CAL_SIT_SAM_NAME"] = row_dict['SIT_TYPE_VAL']

                if calc_sit.find(f".//{namespace}diagnosisCode") is not None:
                    if calc_sit_level == get_element_level(
                            calc_sit.find(f".//{namespace}diagnosisCode")):
                        row_dict["DX"] = (calc_sit.find(f".//{namespace}diagnosisCode")).get('id')
                        row_dict["DX_DESC"] = (calc_sit.find(f".//{namespace}diagnosisCode")).get('desc')
                    else:
                        row_dict["DX"], row_dict["DX_DESC"] = None, None
                else:
                    row_dict["DX"], row_dict["DX_DESC"] = None, None

                if (calc_sit.find(f".//{namespace}placeOfServiceType")) is not None:
                    if calc_sit_level == get_element_level(
                            calc_sit.find(f".//{namespace}placeOfServiceType")):
                        row_dict['POS'] = (calc_sit.find(f".//{namespace}placeOfServiceType")).get(
                            'id')
                        row_dict['POS_DESC'] = (
                            calc_sit.find(f".//{namespace}placeOfServiceType")).get(
                            'desc')
                else:
                    row_dict['POS'], row_dict["POS_DESC"] = None, None

                if (calc_sit.find(f".//{namespace}specialtyCode")) is not None:
                    if calc_sit_level == get_element_level(
                            calc_sit.find(f".//{namespace}specialtyCode")):
                        row_dict['SPEC'] = (calc_sit.find(f".//{namespace}specialtyCode")).get('id')
                        row_dict['SPEC_DESC'] = (calc_sit.find(f".//{namespace}specialtyCode")).get(
                            'desc')
                    else:
                        row_dict['SPEC'], row_dict["SPEC_DESC"] = None, None
                else:
                    row_dict['SPEC'], row_dict["SPEC_DESC"] = None, None

                if (calc_sit.find(f".//{namespace}situationGroup")) is not None:
                    sit_grp = calc_sit.find(f".//{namespace}situationGroup")
                    sit_grp_level = get_element_level(sit_grp)
                    if calc_sit_level == sit_grp_level:
                        row_dict['SIT_GRP_ID'] = (calc_sit.find(f".//{namespace}situationGroup")).get('id')
                        row_dict['SIT_GRP_DESC'] = (calc_sit.find(f".//{namespace}situationGroup")).get('desc')

                        if (calc_sit.find(f".//{namespace}calculationType")) is not None:
                            if sit_grp_level == get_element_level(calc_sit.find(f".//{namespace}calculationType")):
                                row_dict["CAL_TYPE_VAL"] = (calc_sit.find(f".//{namespace}calculationType")).\
                                    get('value')

                        if (calc_sit.find(f".//{namespace}:examinerActionCode")) is not None:
                            if sit_grp_level == get_element_level(
                                    calc_sit.find(f".//{namespace}examinerActionCode")):
                                row_dict["EXAM_ACT_VAL"] = (
                                    calc_sit.find(f".//{namespace}examinerActionCode")).get('value')
                                row_dict["EXAM_ACT_DESC"] = (
                                    calc_sit.find(f".//{namespace}examinerActionCode")).get('desc')
                        else:
                            row_dict["EXAM_ACT_VAL"] = None
                            row_dict["EXAM_ACT_DESC"] = None

                        if len(sit_grp.findall(f".//{namespace}calculationStep")) > 0:
                            for benefit_option in sit_grp.findall(f".//{namespace}benefitOption"):
                                if benefit_option.find(f".//{namespace}benefitType").get("value") == "Coinsurance":
                                    row_dict["COIN"] = "Yes"
                                    row_dict["COIN_BO_NAME"] = benefit_option.get("name")
                                    row_dict["COIN_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["COIN_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["COIN_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["COIN_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get(
                                        'value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['COIN_ACCUM'] = benefit_option.find(f".//{namespace}claimsAccumulatorName")\
                                            .get('value')
                                    else:
                                        row_dict['COIN_ACCUM'] = None

                                    row_dict['COIN_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')

                                elif benefit_option.find(f".//{namespace}benefitType").get("value") == "Copayment":
                                    benefit = benefit_option.find(f".//{namespace}benefitType")
                                    row_dict["COPAY"] = "Yes"
                                    row_dict["COPAY_BO_NAME"] = benefit_option.get("name")
                                    row_dict["COPAY_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["COPAY_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["COPAY_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["COPAY_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get(
                                        'value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['COPAY_ACCUM'] = benefit_option.find(f".//{namespace}claimsAccumulatorName").get(
                                            'value')
                                    else:
                                        row_dict['COPAY_ACCUM'] = None

                                    row_dict['COPAY_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')
                                    row_dict['COPAY_MAX'] = None
                                    row_dict['COPAY_MAX_BO_NAME'] = None
                                    row_dict['COPAY_MAX_BO_DESC'] = None
                                    row_dict['COPAY_MAX_VAL'] = None
                                    row_dict['COPAY_MAX_PERIOD'] = None
                                    row_dict['COPAY_MAX_VAL'] = None
                                    row_dict['COPAY_MAX_EOB'] = None
                                    row_dict['COPAY_MAX_ACCUM'] = None
                                    row_dict['COPAY_MAX_ACCUM_NET'] = None

                                elif benefit_option.get("name") == "DedINNT1IndMed":
                                    row_dict["DED"] = "Yes"
                                    row_dict["DED_BO_NAME"] = benefit_option.get("name")
                                    row_dict["DED_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["DED_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["DED_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["DED_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get('value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['DED_ACCUM'] = benefit_option.find(f".//{namespace}claimsAccumulatorName").get(
                                            'value')
                                    else:
                                        row_dict['DED_ACCUM'] = None

                                    row_dict['DED_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')

                                elif benefit_option.get("name") == "DedINNT1FamMed":
                                    row_dict["DED_AGG"] = "Yes"
                                    row_dict["DED_AGG_BO_NAME"] = benefit_option.get("name")
                                    row_dict["DED_AGG_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["DED_AGG_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["DED_AGG_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["DED_AGG_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get(
                                        'value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['DED_AGG_ACCUM'] = benefit_option.find(
                                            f".//{namespace}claimsAccumulatorName").get('value')
                                    else:
                                        row_dict['DED_AGG_ACCUM'] = None

                                    row_dict['DED_AGG_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')

                                elif benefit_option.find(f".//{namespace}benefitType").get("value") == "DollarLimit":
                                    row_dict["DOL_LMT"] = "Yes"
                                    row_dict["DOL_LMT_BO_NAME"] = benefit_option.get("name")
                                    row_dict["DOL_LMT_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["DOL_LMT_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["DOL_LMT_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["DOL_LMT_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get(
                                        'value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['DOL_LMT_ACCUM'] = benefit_option.find(
                                            f".//{namespace}claimsAccumulatorName").get(
                                            'value')
                                    else:
                                        row_dict['DOL_LMT_ACCUM'] = None

                                    row_dict['DOL_LMT_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')

                                elif benefit_option.find(f".//{namespace}benefitType").get(
                                        "value") == "Unit":
                                    row_dict["UNIT"] = "Yes"
                                    row_dict["UNIT_BO_NAME"] = benefit_option.get("name")
                                    row_dict["UNIT_BO_DESC"] = benefit_option.get("desc")
                                    row_dict["UNIT_VAL"] = benefit_option.find(f".//{namespace}benefitValue").text
                                    row_dict["UNIT_PERIOD"] = benefit_option.find(f".//{namespace}benefitPeriod").get(
                                        'value')
                                    row_dict["UNIT_EOB"] = float(benefit_option.find(f".//{namespace}eobCode").get(
                                        'value'))
                                    if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                        row_dict['UNIT_ACCUM'] = benefit_option.find(f".//{namespace}claimsAccumulatorName").get(
                                            'value')
                                    else:
                                        row_dict['UNIT_ACCUM'] = None

                                    row_dict['UNIT_ACCUM_NET'] = benefit_option.find(f".//{namespace}accumNetworkType").get(
                                        'value')
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
                            del row_dict

                            # print(row_dict)



                        else:
                            rows_list.append(row_dict)
                            del row_dict

    if flagx:
        row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                    "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": int(ele.get("level")),
                    "PATH_BEN_COMP_NAME": (getpath(ele))[0], "PATH_BEN_COMP_DESC": (getpath(ele))[1],
                    'SVC_DEF_ID': ele.find(f".//{namespace}serviceDefinition").get('id'),
                    'SVC_DEF_DESC': ele.find(f".//{namespace}serviceDefinition").get('desc')}
        rows_list.append(row_dict)
        del row_dict

print(f"Total rows {len(rows_list)}")

xml_df = pd.DataFrame(rows_list)

xml_df.to_excel("output/xml_data.xlsx")
xml_df.reset_index(level=0, inplace=True)
xml_df.rename({"index": "id"}, axis=1, inplace=True)
xml_df.replace(to_replace=[None], value=np.nan, inplace=True)

excel_df.reset_index(level=0, inplace=True)
excel_df.rename({"index": "id"}, axis=1, inplace=True)
excel_df.replace(to_replace=[None], value=np.nan, inplace=True)
#
new_df = pd.DataFrame()
column_list = []
matched = []
not_matched = []

# new_df.to_excel("sd.xlsx")


# print(pd.DataFrame([xml_df["COIN_EOB"].astype(str), excel_df["COIN_EOB"].astype(str),
#                     xml_df["COIN_EOB"].astype(str) == excel_df["COIN_EOB"].astype(str)]))


df3 = pd.merge(xml_df, excel_df, how="outer", on=["id"], indicator=True, suffixes=('_xml', '_xl'))

final_df = pd.DataFrame()
comparison_columns = ["id"]
for column in xml_df.columns:
    if column != 'id':
        df3[column + "_match"] = df3[column + "_xml"].astype(str) == df3[column + "_xl"].astype(str)
        comparison_columns.extend([column + "_xml", column + "_xl", column + "_match"])
        column_list.append(column)
        matched.append(df3[column + "_match"].sum())
        not_matched.append((~df3[column + "_match"]).sum())

final_df = df3[comparison_columns]
pd.options.mode.chained_assignment = None
for column in xml_df.columns:
    if column != 'id':
        final_df[column + "_match"].replace(to_replace=[True, False], value=["Yes", "No"], inplace=True)
        # final_df[column + "_match"].replace(to_replace=False, value="No", inplace=True)

stats = {
    "Columns": column_list, "Match Count": matched, "Mismatch Count": not_matched
}

stats_df = pd.DataFrame(stats)
stats_df.reset_index(level=0, inplace=True)
stats_df.rename({"index": "id"}, axis=1, inplace=True)

with pd.ExcelWriter('../output_files/xml_vs_xl.xlsx', engine='openpyxl', mode='w') as writer:
    final_df.to_excel(writer, sheet_name="Comparison", index=False)
    stats_df.to_excel(writer, sheet_name="Stats", index=False)

print(final_df)
