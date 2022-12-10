# from utils.duplicateIdentificationUtils import duplicateIdentification
#
# obj = duplicateIdentification("SAM_ARTIFACTS/common_report/duplicate_nodes_common_report.xlsx")
#
# output = obj.sibling_duplicate_data_identification()
#
# df['qa_verdict_match'] = df[['change_sit_list', 'qa_verdict_on_changed_sit']].apply(
#             lambda a: "Yes" if a['change_sit_list'] == a['qa_verdict_on_changed_sit'] else "No", axis=1)
#
# print(output)

A = {1, 2}
B = {4, 3, 1, 2}

print(A.union(B) == B)
