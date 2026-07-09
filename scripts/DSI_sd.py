import sys
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from time import time
import io
from collections import OrderedDict

def build_dict(raw_dlog_fn):
    """
    Builds dictionary from raw datalog
    :param raw_dlog_fn: File path to raw datalog
    :return: Datalog dictionary
    """
    dlog_dict = {}

    ipf = open (raw_dlog_fn,"r",encoding="utf8")
    for line in ipf:
        if "ITUFF_LIMIT" in line:
            dlog_dict["LIMIT_LINERATE"] = ('str', line.replace('##ITUFF_LIMIT##','').strip("\n"))
        if "ITUFF_VALUE" in line:
            dlog_dict["READ_LINERATE"] = ('str', line.replace('##ITUFF_VALUE##','').strip("\n"))

    ipf.close()
    return dlog_dict

def gettestname():

    ipf = open (raw_dlog_fn,"r",encoding="utf8")
    for line in ipf:
        if "ITUFF_TOKEN" in line:
            testname = line.replace('##ITUFF_TOKEN##','').strip("\n")
   
    return testname

def build_xml_tree(root, x_dict):
    """
    Add elements to the XML tree
    :param root: XML tree or sub-tree root
    :param dict: Dictionary with tage names and values
    :return: None
    """
    for k in sorted(x_dict.keys()):
        v = x_dict[k]
        if isinstance(v, dict):
            node = ET.SubElement(root, k)
            build_xml_tree(node, v)
        else:
            assert (isinstance(v, tuple))
            vtype = v[0]
            value = v[1]
            if vtype == 'bin' or vtype == 'hex':
                node = ET.SubElement(root, k, attrib={'type': vtype})
            else:
                node = ET.SubElement(root, k)
            node.text = value

def write_struct_dlog(test_name, dlog_dict, struct_dlog_fn):
    """
    Write dictionary as structured datalog
    :param test_name: Name of the test
    :param dlog_dict: Dictionary containing relevant information to datalog
    :param struct_dlog_fn: File path to structure datalog
    :return: None
    """
    test = ET.Element('ITUFF', attrib={'name': test_name})
    build_xml_tree(test, dlog_dict)
    rough_string = ET.tostring(test, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(struct_dlog_fn, 'w') as opf:
        opf.write(reparsed.toprettyxml(indent="\t"))

if __name__ == '__main__':
    try:
        start = time()
        # get command line inputs and validate them
        if len(sys.argv) != 4:
            print("ERROR: Incorrect usage")
            print("Expected: python.exe DSI_sd.py <test name> <raw datalog file path> <structure datalog file path>")
            sys.exit(1)
        test_name = sys.argv[1]
        raw_dlog_fn = sys.argv[2]
        struct_dlog_fn = sys.argv[3]
        if not os.path.exists(raw_dlog_fn):
            print("ERROR: Raw datalog does not exist. Please check file path")
            sys.exit(1)
        if not os.path.exists(os.path.dirname(struct_dlog_fn)):
            print("ERROR: Structured datalog file path is incorrect. Please check file path")
            sys.exit(1)
        #replace test_name
        test_name = gettestname()
        # build dictionary from raw datalog
        dlog_dict = build_dict(raw_dlog_fn)
        # write dictionary as structured datalog
        write_struct_dlog(test_name, dlog_dict, struct_dlog_fn)
        # print elapsed time
        end = time()
        print("Time taken: ", end - start, "seconds")
    except Exception as e:
        print("ERROR: Script failed:", str(e))