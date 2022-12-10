from lxml import etree as et
import pandas as pd

namespaces = {"ns5": "http://wellpoint.com/schema/pushPlanRequest/v1"}

tree = et.parse("input/31KT_Plan.xml")
root = tree.getroot()

xml_data_list = []
for ele in root.findall(".//ns5:benefitComponent", namespaces=namespaces):
    element_level = int(ele.get("level"))
    if element_level == 1:
        ele_attr_dict = {"BEN_COMP_NAME": ele.get("name"), "BEN_COMP_LVL": ele.get("level"),
                         "PATH_BEN_COMP_NAME": ele.get("name")}
        xml_data_list.append(ele_attr_dict)
    else:
        path_list = list()
        path_list.append(ele.get("name"))
        ele1 = ele
        while element_level > 1:
            prt = ele1.getparent().getparent()
            path_list.append(prt.get("name"))
            element_level = int(prt.get("level"))
            ele1 = prt
        ele_path = ""
        for item in path_list[::-1]:
            ele_path = ele_path + ">" + item
        ele_attr_dict = {"BEN_COMP_NAME": ele.get("name"), "BEN_COMP_LVL": ele.get("level"),
                         "PATH_BEN_COMP_NAME": ele_path[1:]}
        xml_data_list.append(ele_attr_dict)

df = pd.DataFrame(xml_data_list)
df.to_excel("output/xml_test.xlsx")

df1 = pd.read_excel("input/Benefit Details - Template.xlsx", sheet_name="Benefits")
df2 = df1[["BEN_COMP_NAME", "BEN_COMP_LVL", 'PATH_BEN_COMP_NAME']]

df3 = pd.merge(df, df2, how="outer", on=["PATH_BEN_COMP_NAME", "BEN_COMP_NAME"], indicator=True, suffixes=('_xml', '_xl'))
result = df3[(df3["BEN_COMP_LVL_xl"].isna()) | (df3["BEN_COMP_LVL_xml"].isna())]
print(result)
result.to_excel("output/output.xlsx")
