"""AnthemEM Test Suite"""

from utils.duplicateIdentificationUtils import duplicateIdentification
from utils.outXmlValidationUtils import outPutxmlCheck
from utils.commonExcelValidationUtils import commonReportCheck
import pytest_check as check


class TestAnthem:
    """AnthemEM Test Suite"""

    def test_verify_outputXML(self):
        """TC01 Validating Output XML file"""
        outXMlCheck = outPutxmlCheck('SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx',
                                     'SAM_ARTIFACTS/transformed_xml/31KT_Plan_Transformed.xml')

        result_dict = outXMlCheck.checkValidations()
        flag = False
        failed_list = []
        for k, v in result_dict.items():
            # assert result_dict[k] is True, f"for column {k}, the value is {result_dict[k]}"
            check.is_true(v, msg="Not True")
            if not v:
                print(f"for column {k}, the value is {result_dict[k]}")
                failed_list.append(k)
                flag = True
        if flag:
            failed_columns = " ".join(item for item in failed_list)
            raise AssertionError(f"\nfor {failed_columns} columns the values are not as expected")

    def test_verify_commonReport(self):
        """TC02 Validating Common report data against input XML data"""
        CommReportCheck = commonReportCheck('SAM_ARTIFACTS/input_xml/31KT_Plan.xml',
                                            'SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx')

        output = CommReportCheck.validateXmlData()
        column_mismatch_dict = output[0]
        output_file = output[1]
        flag = False
        failed_list = []
        for k, v in column_mismatch_dict.items():
            # print(k, v)
            # assert column_mismatch_dict[k] == 0, f"for column {k}, the mismatch count is {column_mismatch_dict[k]}"
            check.equal(0, v, msg="Not Zero")
            if column_mismatch_dict[k] != 0:
                print(f"for column {k}, the mismatch count is {column_mismatch_dict[k]}")
                flag = True
                failed_list.append(k)
        if flag:
            failed_columns = " ".join(item for item in failed_list)
            raise AssertionError(f"\nIn Columns {failed_columns} there were mismatches when the Excel report "
                                 f"was compared with the XML Data.\n Please refer to the "
                                 f"file located at {output_file} for more details")

    def test_verify_sibing_duplicates(self):
        """TC03 Validating the Sibling duplicates in the common report against the input XML data"""
        obj = duplicateIdentification("SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx")

        output = obj.sibling_duplicate_data_identification()
        duplicates_mismatch_count = output[0]
        cal_sit_count = output[1]
        filename = output[2]

        assert duplicates_mismatch_count == 0, f"\n{duplicates_mismatch_count} mismatches have occurred for " \
                                               f"{cal_sit_count} Calculation Situations, " \
                                               f"Please refer file located at {filename} for details "
