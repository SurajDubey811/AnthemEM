import xml.etree.ElementTree as ET
import re


def getNamespace(element):
    """
    Description: This function returns the namespace from the XML for the input ElementTree element
    :param element: ElementTree element
    :return: namespace of the input ElementTree element
    """
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def get_calcSIT_xpath(ben_comp_path, namespace):
    """
    Description: This function generates the xpath of the input ElementTree element
    :param ben_comp_path: ben_comp_path of the calculation situation
    :param namespace: namespace of the calculation situation
    :return: Xpath of the input ElementTree element
    """
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
    if len(sit_list) == len(root.findall(xpath)):
        verdict = 'Yes'
    else:
        if all(i != i for i in sit_list):
            verdict = 'Yes'
        else:
            verdict = 'No'
    return len(sit_list), len(root.findall(xpath)), verdict, xpath


def getpath(elem):
    """
    Description: This function generates the Path of the Benefit component element
    from the first Benefit component parent
    :param elem: ElementTree element
    :return: Path of the Benefit component element
    """
    element_level = int(elem.get("level"))
    if element_level == 1:
        name_path = elem.get('name')
        desc_path = elem.get("desc")

    else:
        name_path_list = list()
        desc_path_list = list()
        name_path_list.append(elem.get("name"))
        desc_path_list.append(elem.get('desc'))
        ele1 = elem
        while element_level > 1:
            prt = ele1.getparent().getparent()
            name_path_list.append(prt.get("name"))
            desc_path_list.append(prt.get("desc"))
            element_level = int(prt.get("level"))
            ele1 = prt
        name_path = ""
        for item in name_path_list[::-1]:
            name_path = name_path + ">" + item
        desc_path = ""
        for item in desc_path_list[::-1]:
            desc_path = desc_path + ">" + item

        name_path = name_path[1:]
        desc_path = desc_path[1:]
    return name_path, desc_path


def get_element_level(element):
    """
    Description: This function retrieves the level attribute of the ElementTree element
    if the element is benefitComponent it returns the level attribute value
    if the element is not benefitComponent, it returns the level attribute value of it's parent benefitComponent
    :param element: ElementTree element
    :return: level attribute of the ElementTree element
    """
    while "benefitComponent" not in element.tag:
        element = element.getparent()
    return element.get('level')


def getExpUpdatePropCount(spec_list, col, value):
    allCount = 0
    for i in spec_list:
        if i["BEN_COMP_CHANGED"] == "deletion" or i["CAL_SIT_CHANGED"] == "deletion":
            pass
        else:
            if i["CAL_SIT_CHANGED"] == "updation":
                allCount += 1
            elif i[col] == value:
                allCount += 1
    return allCount
