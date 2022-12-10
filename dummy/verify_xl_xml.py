import pandas as pd
from lxml import etree as et
from utils.anthemUtils import getpath

tree = et.parse("SAM_ARTIFACTS/input_xml/31KT_Plan.xml")
root = tree.getroot()

namespaces = {"ns5": "http://wellpoint.com/schema/pushPlanRequest/v1"}

PlanID = root.find(".//ns5:planID", namespaces=namespaces).text
PLAN_PROXY_ID = root.find(".//ns5:planProxyID", namespaces=namespaces).text

summ = sum1 = calc_sits = ben_comps = ben_compx = 0
rows_list = list()

for ele in root.findall(".//ns5:benefitComponent", namespaces=namespaces):
    ben_comp_level = ele.get("level")
    ben_comps += 1
    row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": int(ele.get("level"))}
    element_level = int(ele.get("level"))

    row_dict["PATH_BEN_COMP_NAME"], row_dict["PATH_BEN_COMP_DESC"] = getpath(ele)
    row_dict['SVC_DEF_ID'] = (ele.find(".//ns5:serviceDefinition", namespaces=namespaces)).get('id')
    row_dict['SVC_DEF_DESC'] = (ele.find(".//ns5:serviceDefinition", namespaces=namespaces)).get('desc')
    row_dict["BEN_COMP_SAM_NAME"] = ele.get('name')
    flagx = True
    if len(ele.findall(".//ns5:calculationSituation", namespaces=namespaces)) > 0:
        for calc_sit in ele.findall(".//ns5:calculationSituation", namespaces=namespaces):
            calc_sit_parent = calc_sit.getparent().getparent()
            calc_sit_level = calc_sit_parent.get("level")
            if ben_comp_level == calc_sit_level:
                flagx = False
                calc_sits += 1
                # if len(calc_sit.findall(".//ns5:calculationStep", namespaces=namespaces)) > 0:
                summ += 1

                row_dict['SIT_TYPE_VAL'] = (calc_sit.find(".//ns5:situationType", namespaces=namespaces)).get(
                    'value')

                if (calc_sit.find(".//ns5:diagnosisCode", namespaces=namespaces)) is not None:
                    row_dict["DX"] = (calc_sit.find(".//ns5:diagnosisCode", namespaces=namespaces)).get('id')
                    row_dict["DX_DESC"] = (calc_sit.find(".//ns5:diagnosisCode", namespaces=namespaces)).get('desc')
                else:
                    row_dict["DX"], row_dict["DX_DESC"] = None, None
                if (calc_sit.find(".//ns5:placeOfServiceType", namespaces=namespaces)) is not None:
                    row_dict['POS'] = (calc_sit.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get('id')
                    row_dict['POS_DESC'] = (calc_sit.find(".//ns5:placeOfServiceType", namespaces=namespaces)).get(
                        'desc')
                else:
                    row_dict['POS'], row_dict["POS_DESC"] = None, None

                if (calc_sit.find(".//ns5:specialtyCode", namespaces=namespaces)) is not None:
                    row_dict['SPEC'] = (calc_sit.find(".//ns5:specialtyCode", namespaces=namespaces)).get('id')
                    row_dict['SPEC_DESC'] = (calc_sit.find(".//ns5:specialtyCode", namespaces=namespaces)).get(
                        'desc')
                else:
                    row_dict['SPEC'], row_dict["SPEC_DESC"] = None, None

                row_dict["CAL_SIT_SAM_NAME"] = row_dict['SIT_TYPE_VAL']

                if (calc_sit.find(".//ns5:situationGroup", namespaces=namespaces)) is not None:
                    row_dict['SIT_GRP_ID'] = (calc_sit.find(".//ns5:situationGroup", namespaces=namespaces)). \
                        get('id')
                    row_dict['SIT_GRP_DESC'] = (calc_sit.find(".//ns5:situationGroup", namespaces=namespaces)).get(
                        'desc')
                else:
                    row_dict['SIT_GRP_ID'], row_dict["SIT_GRP_DESC"] = None, None
                row_dict["CAL_TYPE_VAL"] = (calc_sit.find(".//ns5:calculationType", namespaces=namespaces)).get(
                    'value')

                if (calc_sit.find(".//ns5:examinerActionCode", namespaces=namespaces)) is not None:
                    row_dict["EXAM_ACT_VAL"] = (
                        calc_sit.find(".//ns5:examinerActionCode", namespaces=namespaces)).get(
                        'value')
                    row_dict["EXAM_ACT_DESC"] = (
                        calc_sit.find(".//ns5:examinerActionCode", namespaces=namespaces)).get(
                        'desc')
                else:
                    row_dict["EXAM_ACT_VAL"] = None
                    row_dict["EXAM_ACT_DESC"] = None
                if len(calc_sit.findall(".//ns5:calculationStep", namespaces=namespaces)) > 0:

                    for benefit_option in calc_sit.findall(".//ns5:calculationStep", namespaces=namespaces):

                        if benefit_option.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Coinsurance":
                            row_dict["COIN"] = "Yes"
                            row_dict["COIN_BO_NAME"] = benefit_option.get("name")
                            row_dict["COIN_BO_DESC"] = benefit_option.get("desc")
                            row_dict["COIN_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["COIN_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod", namespaces=namespaces).get(
                                'value')
                            row_dict["COIN_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['COIN_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                             namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['COIN_ACCUM'] = None

                            row_dict['COIN_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                             namespaces=namespaces).get(
                                'value')

                        if benefit_option.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Copayment":
                            row_dict["COPAY"] = "Yes"
                            row_dict["COPAY_BO_NAME"] = benefit_option.get("name")
                            row_dict["COPAY_BO_DESC"] = benefit_option.get("desc")
                            row_dict["COPAY_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["COPAY_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod",
                                                                           namespaces=namespaces).get(
                                'value')
                            row_dict["COPAY_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['COPAY_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                              namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['COPAY_ACCUM'] = None

                            row_dict['COPAY_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                              namespaces=namespaces).get(
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

                        if benefit_option.get("name") == "DedINNT1IndMed":
                            row_dict["DED"] = "Yes"
                            row_dict["DED_BO_NAME"] = benefit_option.get("name")
                            row_dict["DED_BO_DESC"] = benefit_option.get("desc")
                            row_dict["DED_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["DED_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod", namespaces=namespaces).get(
                                'value')
                            row_dict["DED_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['DED_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                            namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['DED_ACCUM'] = None

                            row_dict['DED_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                            namespaces=namespaces).get(
                                'value')

                        if benefit_option.get("name") == "DedINNT1FamMed":
                            row_dict["DED_AGG"] = "Yes"
                            row_dict["DED_AGG_BO_NAME"] = benefit_option.get("name")
                            row_dict["DED_AGG_BO_DESC"] = benefit_option.get("desc")
                            row_dict["DED_AGG_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["DED_AGG_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod",
                                                                             namespaces=namespaces).get(
                                'value')
                            row_dict["DED_AGG_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['DED_AGG_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                                namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['DED_AGG_ACCUM'] = None

                            row_dict['DED_AGG_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                                namespaces=namespaces).get(
                                'value')

                        if benefit_option.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "DollarLimit":
                            row_dict["DOL_LMT"] = "Yes"
                            row_dict["DOL_LMT_BO_NAME"] = benefit_option.get("name")
                            row_dict["DOL_LMT_BO_DESC"] = benefit_option.get("desc")
                            row_dict["DOL_LMT_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["DOL_LMT_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod",
                                                                             namespaces=namespaces).get(
                                'value')
                            row_dict["DOL_LMT_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['DOL_LMT_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                                namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['DOL_LMT_ACCUM'] = None

                            row_dict['DOL_LMT_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                                namespaces=namespaces).get(
                                'value')

                        if benefit_option.find(".//ns5:benefitType", namespaces=namespaces).get("value") == "Unit":
                            row_dict["UNIT"] = "Yes"
                            row_dict["UNIT_BO_NAME"] = benefit_option.get("name")
                            row_dict["UNIT_BO_DESC"] = benefit_option.get("desc")
                            row_dict["UNIT_VAL"] = float(
                                benefit_option.find(".//ns5:benefitValue", namespaces=namespaces).text)
                            row_dict["UNIT_PERIOD"] = benefit_option.find(".//ns5:benefitPeriod", namespaces=namespaces).get(
                                'value')
                            row_dict["UNIT_EOB"] = int(
                                benefit_option.find(".//ns5:eobCode", namespaces=namespaces).get('value'))
                            if benefit_option.find(".//ns5:claimsAccumulatorName", namespaces=namespaces) is not None:
                                row_dict['UNIT_ACCUM'] = benefit_option.find(".//ns5:claimsAccumulatorName",
                                                                             namespaces=namespaces).get(
                                    'value')
                            else:
                                row_dict['UNIT_ACCUM'] = None

                            row_dict['UNIT_ACCUM_NET'] = benefit_option.find(".//ns5:accumNetworkType",
                                                                             namespaces=namespaces).get(
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

                else:
                    rows_list.append(row_dict)
                    sum1 += 1

    if flagx:
        ben_compx += 1
        rows_list.append(row_dict)

# stats = [{"calc steps present in calc situations": summ, "calc steps not present in calc situations": sum1,
#           "total calc situations": calc_sits,
#           "total benefit components without any direct calc_situation children": ben_compx,
#           "total benefit components": ben_comps, "Total Lines": len(rows_list)}]

print(f"calc steps present in calc situations: {summ}")
print(f"calc steps not present in calc situations: {sum1}")

print(f"total calc situations: {calc_sits}")
print(f"total benefit components without any direct calc_situation children: {ben_compx}")
print(f"total benefit components: {ben_comps}")
print(f"Total lines: {len(rows_list)}")

rows_df = pd.DataFrame(rows_list)

stats = [["Total benefit components", ben_comps],
         ["Calc steps present in calc situations", summ],
         ["Calc steps not present in calc situations", sum1],
         ["Total calc situations", calc_sits],
         ["Total benefit components without any direct calc_situation children", ben_compx],
         ["Total Lines", len(rows_list)]]

stats_df = pd.DataFrame(stats, columns=["Stat", "Value"])

stats_df.to_excel("output/stats.xlsx", index=False)

rows_df.to_excel("output/xml_data.xlsx", index=False)

rows_df.reset_index(level=0, inplace=True)
rows_df.rename({"index": "id"}, axis=1, inplace=True)

df2 = pd.read_excel("SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx")

df2.reset_index(level=0, inplace=True)
df2.rename({"index": "id"}, axis=1, inplace=True)

df3 = pd.merge(rows_df, df2, how="outer", on=["id"], indicator=True, suffixes=('_xml', '_xl'))

df3.to_excel("output_files/xml_vs_xl.xlsx", index=None)

comparison_columns = ["id"]
for column in rows_df.columns:
    if column != 'id':
        df3[column + "_match"] = df3[df3[column + "_xml"] == df3[column + "_xl"]]
        comparison_columns.extend([column + "_xml", column + "_xl", column + "_match"])

df3[comparison_columns].to_excel("output_files/xml_vs_xl.xlsx")
