import pandas as pd
import json


class duplicateIdentification:
    def __init__(self, excelFile):
        # reading excel file
        self.excelData = pd.read_excel(excelFile)
        # changing index to 'id' field
        self.excelData['id'] = self.excelData.index
        self.excelData.fillna('', inplace=True)

        with open("config/duplicateIdentification_conf.json") as f:
            duplicate_conf = json.load(f)
            hashCols = duplicate_conf["hashCols"]
            self.priority_rules = duplicate_conf["prop_priority_rule"]
            self.output_report = duplicate_conf["output_report"]
            self.sibling_dup_indentify_req_cols = duplicate_conf["sibling_dup_indentify_req_cols"]
            self.sibling_dup_indentify_on_cols = duplicate_conf["sibling_dup_indentify_on_cols"]
            self.sibling_dup_identified_in_app_col = duplicate_conf["sibling_dup_identified_in_app_col"]

        self.maxPriorityValsDict = dict()
        for keys in self.priority_rules:
            # getting list max priority values
            self.maxPriorityValsDict.update(
                {keys: sorted([i for i in self.priority_rules[keys] if self.priority_rules[keys][i] == 1])})
        # getting column data to generate hash value on Situation Type [ removing blank values]
        self.excelData['group_columns'] = self.excelData[hashCols].apply(
            lambda g: [str(i) for i in g.values.tolist() if str(i) != ''], axis=1)
        # generating hash code
        self.excelData['SIT_GRP_HASH'] = self.excelData['group_columns'].apply(lambda g: hash("".join(g)))
        # adding group has on duplicate identification on columns
        self.sibling_dup_indentify_on_cols.append('SIT_GRP_HASH')
        # setting benefit component group id
        self.excelData['BEN_COMP_NAME_ID'] = self.excelData['PATH_BEN_COMP_NAME'].apply(
            lambda g: self.get_group_id(g, self.excelData['PATH_BEN_COMP_NAME'].values.tolist()))
        # setting parent group id
        self.excelData['parent_group_id'] = self.excelData['PATH_BEN_COMP_NAME'].apply(
            lambda g: self.get_group_id(g, self.excelData['PATH_BEN_COMP_NAME'].values.tolist(), isParent=True))

    def sibling_duplicate_data_identification(self):
        '''
        Description: This function do following:
            1. identifies sibling level duplicates.
            2. compare duplicate identified (QA automation) with application identifed ones
            3. create comparision report
            4. return count of mismatches with report name
        :return: count of mismatch group & calculation situation count with report name
        '''
        excelDataSiblingIdentification = pd.DataFrame(
            self.excelData[['id'] + self.sibling_dup_indentify_req_cols + self.sibling_dup_indentify_on_cols])
        # print(excelDataSiblingIdentification.columns)
        # creating groups on hashcode and storing deletion properties with row no, in a list in "sibling_index_list" column
        df1 = excelDataSiblingIdentification.groupby(self.sibling_dup_indentify_on_cols)[
            ['id'] + self.sibling_dup_indentify_req_cols].apply(lambda g: g.to_dict('records')).reset_index(
            name='sibling_index_list')
        # creating groups on hashcode and storing deletion identified by application
        df2 = excelDataSiblingIdentification.groupby(self.sibling_dup_indentify_on_cols)[
            ['id'] + [self.sibling_dup_identified_in_app_col]].apply(lambda g: g.to_dict('records')).reset_index(
            name='change_sit_list')
        # merging two group dataframe to get data in single dataframe
        df = pd.merge(df1, df2, on=self.sibling_dup_indentify_on_cols)
        # identify duplicate siblings and storing those in data frame column
        df['qa_verdict_on_changed_sit'] = df['sibling_index_list'].apply(lambda g: self.unlessHandlingCheck(g))
        # comparing application and qa verdict
        df['qa_verdict_match'] = df[['change_sit_list', 'qa_verdict_on_changed_sit']].apply(
            lambda a: "Yes" if a['change_sit_list'] == a['qa_verdict_on_changed_sit'] else "No", axis=1)
        # getting mismatch indexes for further reporting
        mismatched_indexs = [j['id'] for i in df[df['qa_verdict_match'] == "No"]['qa_verdict_on_changed_sit'].tolist()
                             for j in i]
        # merging qa identified duplicate and updated calculation situations with main data for reporting
        df4 = pd.merge(excelDataSiblingIdentification, pd.DataFrame(
            [{"id": j["id"], f"EXP_{self.sibling_dup_identified_in_app_col}": j[self.sibling_dup_identified_in_app_col]}
             for i in df['qa_verdict_on_changed_sit'].tolist()
             for j in i]), on='id')
        compCols = ['id'] + self.sibling_dup_indentify_on_cols + self.sibling_dup_indentify_req_cols
        with pd.ExcelWriter(self.output_report, engine='openpyxl') as writer:
            # writing actual mismatch data
            if len(mismatched_indexs) > 0:
                df4[df4.index.isin(mismatched_indexs)][compCols[:compCols.index('CAL_SIT_CHANGED') + 1] + \
                                                       [f"EXP_{self.sibling_dup_identified_in_app_col}"] + \
                                                       compCols[compCols.index('CAL_SIT_CHANGED') + 1:]].to_excel(
                    writer, sheet_name="sibing_mismatch_data", index=None)
                df4[compCols[:compCols.index('CAL_SIT_CHANGED') + 1] + \
                    [f"EXP_{self.sibling_dup_identified_in_app_col}"] + \
                    compCols[compCols.index('CAL_SIT_CHANGED') + 1:]].to_excel(
                    writer, sheet_name="sibing_compare_data", index=None)
            # writing main comparison sheet
            df.to_excel(writer, sheet_name="sibling_group_comparison")
        return df[df['qa_verdict_match'] == "No"].shape[0], df4[df4.index.isin(mismatched_indexs)].shape[
            0], self.output_report

    def get_group_id(self, item, id_list, isParent=False):
        if isParent:
            if ">" not in item:
                return -1
            else:
                parent_id = ">".join(item.split(">")[:-1])
                return list(dict.fromkeys(id_list)).index(parent_id)
        else:
            return list(dict.fromkeys(id_list)).index(item)

    def unlessHandlingCheck(self, listProps):
        df = pd.DataFrame(listProps)
        # print(df.columns)
        # print(listProps)
        unlessOtherSpecifiedList = df[df["SIT_TYPE_DESC"] == 'Unless Otherwise Specified'].index
        df_unless = df[df.index.isin(unlessOtherSpecifiedList)]
        # print(json.dumps(listProps,indent=1),df_unless.shape[0])
        if df_unless.shape[0] >= 1:
            unless_id_dict_occurance = {}

            for prop in self.priority_rules:
                if prop != 'POS':
                    df_unless_set_dx_id = \
                    df[df[prop].isin([k for k in self.priority_rules[prop] if self.priority_rules[prop][k] == 1])][
                        'id'].tolist()
                    for j in df_unless_set_dx_id:
                        if j not in unless_id_dict_occurance:
                            unless_id_dict_occurance.update({j: 1})
                        else:
                            unless_id_dict_occurance[j] += 1
            if len(set(df["POS"].tolist())) == 1:
                unlessOther_threshold = 1
            else:
                unlessOther_threshold = 2
            commonUnlessCOls = [i for i in unless_id_dict_occurance if unless_id_dict_occurance if
                                unless_id_dict_occurance[i] >= unlessOther_threshold]
            df_unless_set = pd.DataFrame(df[df['id'].isin(commonUnlessCOls)])
            # print(set(df["POS"].tolist()),unlessOther_threshold)
            # print(df_unless_set)
            df_unless_set[self.sibling_dup_identified_in_app_col] = df_unless_set["SIT_TYPE_DESC"].apply(
                lambda g: "deletion" if g != 'Unless Otherwise Specified' else "")
            df_not_unless_set = df[~df['id'].isin(commonUnlessCOls)]

            # print(df_unless_set.shape[0])
            # print(df_not_unless_set.shape[0])
            unless_validation_data = df_unless_set[['id', self.sibling_dup_identified_in_app_col]].to_dict("records")
            if df_not_unless_set.shape[0] >= 1:
                unless_validation_data += self.checkDuplicateCalSit(df_not_unless_set.to_dict("records"))
            return pd.DataFrame(unless_validation_data).sort_values(by=["id"], ascending=True).to_dict("records")
        else:
            return self.checkDuplicateCalSit(listProps)

    def checkDuplicateCalSit(self, listProps):
        '''
        Description: This function analyze list of properties/creteria and predicts deletion/ updation status of each row/calculation situation type
        :param listProps: list of row numbers, columns data required for duplicate identification e.g.
        [{'id': 275, 'DX': '', 'POS': 'HOMEPOS', 'SPEC': 'SPC', 'SIT_TYPE_DESC': 'Home by a Specialist'},
        {'id': 277, 'DX': '', 'POS': 'INDPCLPOS', 'SPEC': 'SPC', 'SIT_TYPE_DESC': 'Independent Clinic by a Specialist'},
        {'id': 279, 'DX': '', 'POS': 'OFFICEPOS', 'SPEC': 'SPC', 'SIT_TYPE_DESC': 'Office by a Specialist'}]
        :return: qa verdict in list of dictionary containing row id and status of the column (.e.g. deletion, updation)
        '''
        # converting duplicate identification list of properties to dataframe
        df = pd.DataFrame(listProps)
        propColDupData = {}

        for keys in self.priority_rules:
            # creating group by dataframe to list row no and single property level qa verdict group by property value
            grp_df = df.groupby([keys], sort=False)[['id']].apply(
                lambda g: [
                    dict(i, **{"action": ""}) if g.to_dict('records')[0] == i else dict(i, **{"action": "deletion"})
                    for i in g.to_dict('records')]).reset_index(name='index_list')
            # only consider the property if more than unique one value exist in the group
            if grp_df.shape[0] > 1:
                # need to consider the creteria only if some specialized
                # value exist in group which might be deleted
                if sorted(grp_df[keys].tolist()) != self.maxPriorityValsDict[keys]:
                    # getting property level consolidated SIT change status
                    data = self.delete_mark(grp_df.set_index(keys).to_dict()['index_list'], keys)
                    propColDupData.update({keys: data})
        identifiedProps = list(propColDupData.keys())
        finalVerdict = []
        # print(propColDupData)
        # consolidation of SIT changes status based on different sibling duplication identification properties
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
                    finalVerdict.append({"id": keys, self.sibling_dup_identified_in_app_col: "deletion"})
                else:
                    if "updation" in row_del_stat:
                        if "deletion" not in row_del_stat:
                            finalVerdict.append({"id": keys, self.sibling_dup_identified_in_app_col: "updation"})
                        else:
                            finalVerdict.append({"id": keys, self.sibling_dup_identified_in_app_col: "deletion"})
                    else:
                        finalVerdict.append({"id": keys, self.sibling_dup_identified_in_app_col: ""})
        if len(finalVerdict) == 0:
            return [{'id': i['id'], self.sibling_dup_identified_in_app_col: ""} for i in listProps]
        else:
            return finalVerdict

    def delete_mark(self, colDict, keys):
        '''
        This function consolidate duplication identification properties value wise SIT change status
        and return dictionary of row id and corrosponding SIT change status
        :param colDict: dictionary associated with duplication identification
        properties value with row id and current SIT status
        :param keys: sibling duplication identification properties
        :return: dictionary of row id and corrosponding SIT change status
        '''
        # creating function to get priority of any property value
        h = lambda g: self.priority_rules[keys][g] if g in self.priority_rules[keys] else max(
            self.priority_rules[keys].values()) + 1
        colValues = list(colDict.keys())
        minweight = min([h(i) for i in colValues])
        dd = dict()
        tempDD = dict()
        for key, val in colDict.items():
            for i in val:
                tempDD.update({i["id"]: {'val': key, 'action': i['action']}})
        colDataInDict = dict()
        tempDDSortedKeys = sorted(tempDD.keys())
        for key in tempDDSortedKeys:
            colDataInDict.update({key: tempDD[key]})
        for i in range(len(tempDDSortedKeys) - 1):
            # case: to next consecutive value priortiy is decreasing
            if h(colDataInDict[tempDDSortedKeys[i]]['val']) < h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
                # if already generalized
                if colDataInDict[tempDDSortedKeys[i]]['val'] in self.maxPriorityValsDict[keys]:
                    # it's top row then make current status to null else keep existing status
                    if i == 0:
                        colDataInDict[tempDDSortedKeys[i]]['action'] = ''
                else:
                    # if not generalized then status will be updation iff value within rules else keep existing status
                    if colDataInDict[tempDDSortedKeys[i]]['val'] in self.priority_rules[keys]:
                        colDataInDict[tempDDSortedKeys[i]]['action'] = 'updation'
                # if next value within rules
                if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in self.priority_rules[keys]:
                    # if next value is top priority then mark next status as deletion
                    if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in self.maxPriorityValsDict[keys]:
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                    else:
                        # else overwrite it to updation
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'update-delete'
                else:
                    # if value not in rules mark it as deletion
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
            # case: to next consecutive value priortiy is incerasing
            elif h(colDataInDict[tempDDSortedKeys[i]]['val']) > h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
                # set next value to null if it is top priority
                if colDataInDict[tempDDSortedKeys[i + 1]]['val'] in self.maxPriorityValsDict[keys]:
                    colDataInDict[tempDDSortedKeys[i + 1]]['action'] = ''
                    # check previous lower priority to deletion until priority changes
                    for j in list(range(0, i - 1))[::-1]:
                        if h(colDataInDict[tempDDSortedKeys[j]]['val']) == h(colDataInDict[tempDDSortedKeys[i]]['val']):
                            colDataInDict[tempDDSortedKeys[j]]['action'] = 'deletion'
                        else:
                            break
                else:
                    # if value is not top priority
                    if colDataInDict[tempDDSortedKeys[i]]['val'] in self.priority_rules[keys]:
                        # but still exist in rule then mark value with updation
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'updation'
                # if current value in rules
                if colDataInDict[tempDDSortedKeys[i]]['val'] in self.priority_rules[keys]:
                    # and has top priority
                    if colDataInDict[tempDDSortedKeys[i]]['val'] in self.maxPriorityValsDict[keys]:
                        # mark it with deletion
                        colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
                    else:
                        # else override delete with update
                        colDataInDict[tempDDSortedKeys[i]]['action'] = 'update-delete'
                else:
                    # if current value not in rule then mark it with deletion
                    colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
            # case: both current and next value has same priority
            elif h(colDataInDict[tempDDSortedKeys[i]]['val']) == h(colDataInDict[tempDDSortedKeys[i + 1]]['val']):
                # if first element
                if i == 0:
                    # if both value match then
                    if colDataInDict[tempDDSortedKeys[i]]['val'] == colDataInDict[tempDDSortedKeys[i + 1]]['val']:
                        # mark current one with null and next one as deletion
                        colDataInDict[tempDDSortedKeys[i]]['action'] = ''
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                    # if both value not match ( though has same priority) then
                    else:
                        # if current value is not top priority
                        if h(colDataInDict[tempDDSortedKeys[i]]['val']) > minweight:
                            # then mark both of them with deletion
                            colDataInDict[tempDDSortedKeys[i]]['action'] = 'deletion'
                            colDataInDict[tempDDSortedKeys[i + 1]]['action'] = 'deletion'
                        else:
                            # if top priority then make them null
                            colDataInDict[tempDDSortedKeys[i]]['action'] = ''
                            colDataInDict[tempDDSortedKeys[i + 1]]['action'] = ''
                # if not top element in the group
                else:
                    # if not top priority then copy current value to next value
                    if colDataInDict[tempDDSortedKeys[i]]['val'] not in self.maxPriorityValsDict[keys]:
                        colDataInDict[tempDDSortedKeys[i + 1]]['action'] = colDataInDict[tempDDSortedKeys[i]]['action']
        # create dictionary of row no and SIT change status for returning
        for i in colDataInDict:
            dd.update({i: colDataInDict[i]['action']})
        return dd
