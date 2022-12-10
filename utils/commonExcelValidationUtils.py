from lxml import etree as ET
from utils.commonUtils import getNamespace, getpath, get_element_level
import pandas as pd
import numpy as np


class commonReportCheck:

    def __init__(self, xmlFile, excelFile):
        # create element tree object
        self.column_mismatch_dict = None
        self.xml_df = None
        # parsing XML file
        self.tree = ET.parse(xmlFile)
        # loading excel file into dataframe
        self.excel_df = pd.read_excel(excelFile)
        self.excel_df.reset_index(level=0, inplace=True)
        # changing index to 'id' field
        self.excel_df.rename({"index": "id"}, axis=1, inplace=True)
        self.excel_df.replace(to_replace=[None], value=np.nan, inplace=True)

        # get root element
        self.root = self.tree.getroot()
        self.namespace = getNamespace(self.root)
        self.PlanID = self.root.find(f".//{self.namespace}planID").text
        self.PLAN_PROXY_ID = self.root.find(f".//{self.namespace}planProxyID").text
        # rows_list will contain all the calc sit rows extracted from the input xml
        self.rows_list = list()

    def getXmlData(self):
        """
        Description: This Function does following jobs:
            1. Retrieves all the data from the input XML
            2. Stores data for each Calculation situation into a dictionary (row_dict)
            3. appends the data for each calculation situation dictionary to rows_list
            4. Coverts the list of dictionaries i.e. Calculation situaltions to dataframe (xml_df)

        :return: the dataframe containing all the rows extracted from the input XML (xml_df)
        """
        namespace = self.namespace
        PlanID = self.PlanID
        PLAN_PROXY_ID = self.PLAN_PROXY_ID
        # Iterating through all benefitComponent tags
        for ele in self.root.findall(f".//{self.namespace}benefitComponent"):
            ben_comp_level = ele.get("level")
            flagx = True
            # Iterate through all the calculation situations inside the benefit component
            if len(ele.findall(f".//{namespace}calculationSituation")) > 0:
                for calc_sit in ele.findall(f".//{namespace}calculationSituation"):
                    row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                                "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": ele.get("level"),
                                "PATH_BEN_COMP_NAME": (getpath(ele))[0], "PATH_BEN_COMP_DESC": (getpath(ele))[1],
                                'SVC_DEF_ID': ele.find(f".//{namespace}serviceDefinition").get('id'),
                                'SVC_DEF_DESC': ele.find(f".//{namespace}serviceDefinition").get('desc')}
                    calc_sit_level = get_element_level(calc_sit)
                    # The benefit component will have rest of calculation situation
                    # only if it has a direct child as calculation situation
                    if calc_sit_level == ben_comp_level:
                        flagx = False
                        # row_dict['SIT_TYPE_VAL'] = calc_sit.find(f".//{namespace}situationType").get(
                        #     'value')
                        # row_dict['SIT_TYPE_DESC'] = calc_sit.find(f".//{namespace}situationType").get(
                        #     'desc')
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
                                    if sit_grp_level == get_element_level(
                                            calc_sit.find(f".//{namespace}calculationType")):
                                        row_dict["CAL_TYPE_VAL"] = (calc_sit.find(f".//{namespace}calculationType")). \
                                            get('value')

                                if (calc_sit.find(f".//{namespace}examinerActionCode")) is not None:
                                    if sit_grp_level == get_element_level(
                                            calc_sit.find(f".//{namespace}examinerActionCode")):
                                        row_dict["EXAM_ACT_VAL"] = (
                                            calc_sit.find(f".//{namespace}examinerActionCode")).get(
                                            'value')
                                        row_dict["EXAM_ACT_DESC"] = (
                                            calc_sit.find(f".//{namespace}examinerActionCode")).get(
                                            'desc')
                                else:
                                    row_dict["EXAM_ACT_VAL"] = None
                                    row_dict["EXAM_ACT_DESC"] = None

                                if len(sit_grp.findall(f".//{namespace}calculationStep")) > 0:
                                    for benefit_option in sit_grp.findall(f".//{namespace}benefitOption"):
                                        if benefit_option.find(f".//{namespace}benefitType").get(
                                                "value") == "Coinsurance":
                                            row_dict["COIN"] = "Yes"
                                            row_dict["COIN_BO_NAME"] = benefit_option.get("name")
                                            row_dict["COIN_BO_DESC"] = benefit_option.get("desc")
                                            row_dict["COIN_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["COIN_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["COIN_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get(
                                                    'value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['COIN_ACCUM'] = benefit_option.find(
                                                    f".//{namespace}claimsAccumulatorName") \
                                                    .get('value')
                                            else:
                                                row_dict['COIN_ACCUM'] = None

                                            row_dict['COIN_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
                                                'value')

                                        elif benefit_option.find(f".//{namespace}benefitType").get(
                                                "value") == "Copayment":
                                            benefit = benefit_option.find(f".//{namespace}benefitType")
                                            row_dict["COPAY"] = "Yes"
                                            row_dict["COPAY_BO_NAME"] = benefit_option.get("name")
                                            row_dict["COPAY_BO_DESC"] = benefit_option.get("desc")
                                            row_dict["COPAY_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["COPAY_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["COPAY_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get(
                                                    'value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['COPAY_ACCUM'] = benefit_option.find(
                                                    f".//{namespace}claimsAccumulatorName").get(
                                                    'value')
                                            else:
                                                row_dict['COPAY_ACCUM'] = None

                                            row_dict['COPAY_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
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
                                            row_dict["DED_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["DED_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["DED_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get('value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['DED_ACCUM'] = benefit_option.find(
                                                    f".//{namespace}claimsAccumulatorName").get(
                                                    'value')
                                            else:
                                                row_dict['DED_ACCUM'] = None

                                            row_dict['DED_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
                                                'value')

                                        elif benefit_option.get("name") == "DedINNT1FamMed":
                                            row_dict["DED_AGG"] = "Yes"
                                            row_dict["DED_AGG_BO_NAME"] = benefit_option.get("name")
                                            row_dict["DED_AGG_BO_DESC"] = benefit_option.get("desc")
                                            row_dict["DED_AGG_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["DED_AGG_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["DED_AGG_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get(
                                                    'value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['DED_AGG_ACCUM'] = benefit_option.find(
                                                    f".//{self.namespace}claimsAccumulatorName").get('value')
                                            else:
                                                row_dict['DED_AGG_ACCUM'] = None

                                            row_dict['DED_AGG_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
                                                'value')

                                        elif benefit_option.find(f".//{namespace}benefitType").get(
                                                "value") == "DollarLimit":
                                            row_dict["DOL_LMT"] = "Yes"
                                            row_dict["DOL_LMT_BO_NAME"] = benefit_option.get("name")
                                            row_dict["DOL_LMT_BO_DESC"] = benefit_option.get("desc")
                                            row_dict["DOL_LMT_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["DOL_LMT_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["DOL_LMT_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get(
                                                    'value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['DOL_LMT_ACCUM'] = benefit_option.find(
                                                    f".//{namespace}claimsAccumulatorName").get(
                                                    'value')
                                            else:
                                                row_dict['DOL_LMT_ACCUM'] = None

                                            row_dict['DOL_LMT_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
                                                'value')

                                        elif benefit_option.find(f".//{namespace}benefitType").get(
                                                "value") == "Unit":
                                            row_dict["UNIT"] = "Yes"
                                            row_dict["UNIT_BO_NAME"] = benefit_option.get("name")
                                            row_dict["UNIT_BO_DESC"] = benefit_option.get("desc")
                                            row_dict["UNIT_VAL"] = benefit_option.find(
                                                f".//{namespace}benefitValue").text
                                            row_dict["UNIT_PERIOD"] = benefit_option.find(
                                                f".//{namespace}benefitPeriod").get(
                                                'value')
                                            row_dict["UNIT_EOB"] = float(
                                                benefit_option.find(f".//{namespace}eobCode").get(
                                                    'value'))
                                            if benefit_option.find(f".//{namespace}claimsAccumulatorName") is not None:
                                                row_dict['UNIT_ACCUM'] = benefit_option.find(
                                                    f".//{namespace}claimsAccumulatorName").get(
                                                    'value')
                                            else:
                                                row_dict['UNIT_ACCUM'] = None

                                            row_dict['UNIT_ACCUM_NET'] = benefit_option.find(
                                                f".//{namespace}accumNetworkType").get(
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
                                    # append the row data to the rows list
                                    self.rows_list.append(row_dict)
                                    del row_dict

                                else:
                                    # append the row data to the rows list
                                    self.rows_list.append(row_dict)
                                    del row_dict

            if flagx:
                # If the Benefit component does not have a direct child as Calculation situation
                # only below columns shall be filled
                row_dict = {"PLAN_ID": PlanID, 'PLAN_PROXY_ID': PLAN_PROXY_ID, "BEN_COMP_NAME": ele.get('name'),
                            "BEN_COMP_DESC": ele.get("desc"), "BEN_COMP_LVL": int(ele.get("level")),
                            "PATH_BEN_COMP_NAME": (getpath(ele))[0], "PATH_BEN_COMP_DESC": (getpath(ele))[1],
                            'SVC_DEF_ID': ele.find(f".//{namespace}serviceDefinition").get('id'),
                            'SVC_DEF_DESC': ele.find(f".//{namespace}serviceDefinition").get('desc')}

                # append the row data to the rows list
                self.rows_list.append(row_dict)
                del row_dict

        # Creating a dataframe from the list of rows extracted from the input XML
        self.xml_df = pd.DataFrame(self.rows_list)
        self.xml_df.reset_index(level=0, inplace=True)
        # renaming index column to id
        self.xml_df.rename({"index": "id"}, axis=1, inplace=True)
        self.xml_df.replace(to_replace=[None], value=np.nan, inplace=True)

        return self.xml_df

    def validateXmlData(self):
        """
        Description: This function does following:
            1. Save the dataframe extracted from the XML to am Excel file
            2. Compare the dataframe created from the XML data with the Common Report Excel file
            3. Store the comparison report to an Excel file
            4. Generates column wise statistics of Mismatch count for each column into a dictionary.
            5. Store the statistics to an Excel file
        :return: The statistics dictionary and the path of the comparison output file
        """
        # parse input XML and Generate a dataframe from it
        xml_df = self.getXmlData()
        # save the xml_data to Excel file for reference
        xml_df.to_excel("output_files/xml_data.xlsx")
        column_list, matched, not_matched = [], [], []
        pd.options.mode.chained_assignment = None
        # merging XML dataframe with the Common report Excel dataframe
        df3 = pd.merge(xml_df, self.excel_df, how="outer", on=["id"], indicator=True, suffixes=('_xml', '_xl'))
        comparison_columns = ["id"]
        for column in xml_df.columns:
            if column != 'id':
                # comparing data and adding a _match column for each column to show if the data is matching or not
                df3[column + "_match"] = (df3[column + "_xml"].astype(str) == df3[column + "_xl"].astype(str))
                # determine the sequence of columns to be displayed in the comparison dataframe
                comparison_columns.extend([column + "_xml", column + "_xl", column + "_match"])
                column_list.append(column)
                matched.append(df3[column + "_match"].sum())
                not_matched.append((~df3[column + "_match"]).sum())
        # the dataframe created after comparison
        final_df = df3[comparison_columns]

        # replacing True/False values with Yes/No for better consistency
        for column in xml_df.columns:
            if column != 'id':
                final_df[column + "_match"].replace(to_replace=[True, False], value=["Yes", "No"], inplace=True)

        # Creating statistics dictionary
        stats = {
            "Columns": column_list, "Match Count": matched, "Mismatch Count": not_matched
        }

        stats_df = pd.DataFrame(stats)
        stats_df.reset_index(level=0, inplace=True)
        stats_df.rename({"index": "id"}, axis=1, inplace=True)
        output_file = "output_files/xml_vs_xl.xlsx"
        # saving the compared dataframe and statistics dictionary to the same Excel file
        with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
            final_df.to_excel(writer, sheet_name="Comparison", index=False)
            stats_df.to_excel(writer, sheet_name="Stats", index=False)

        test_data = {k: v for k, v in zip(stats["Columns"], stats["Mismatch Count"])}

        return test_data, output_file
