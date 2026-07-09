import os
import sys
import time
import json

init_params = {
            "parsing_version": "5.0",
            "Project": "GRR",
            "IP": "ETH_50G"
            }

metadata    = ["API","BUILD", "Parser", "NAC NVM","FPPS AutoLoad","NIS FW","MNG PHY FW","Serdes PHY FW","FPPS Stepping","CPU"]

state       = ['Mode', 'State', 'Speed']

attributes  = ['loopback-suppress', 'macsec', 'drop-unsecured', 'max-frame-size', 'mii-loopback', 'min-avg-size', 'phy-an37-enable',
                'phy-an-disable-lf-inh-tmr', 'phy-dfx-action', 'phy-fec-corrected-block', 'phy-fec-options', 'phy-fec-mode', 'phy-fec-request',
                'phy-fec-uncorrected-block', 'phy-fec-lock', 'phy-loopback', 'phy-refclk', 'phy-type', 'phy-type-current', 'phy-ignore-nonce',
                'phy-an-lp-basepage', 'phy-timestamp-enable', 'phy-timestamp-1step-enable', 'phy-timestamp-point', 'phy-lt-enable', 'phy-lt-options',
                'phy-peer-delay', 'phy-vsr-enable', 'phy-no-hcd-event', 'phy-channel-type', 'phy-link-up-debouncing', 'port-mask']

link_faults = ['NF', 'LF', 'RF']

ttl         = ['AN retries raw', 'AN retries', 'HCD vld', 'LT done', 'LT dur (ms)', 'Link Up (ms)']

fec_det     = ['T_CW_received', 'T_CW_corrected', 'T_CW_uncorrected', 'corrected_CW_p_0', 'corrected_CW_p_4', 'corrected_CW_p_8', 'corrected_CW_p_12',
                'corrected_CW_p_1', 'corrected_CW_p_5', 'corrected_CW_p_9', 'corrected_CW_p_13', 'corrected_CW_p_2', 'corrected_CW_p_6', 'corrected_CW_p_10',
                'corrected_CW_p_14', 'corrected_CW_p_3', 'corrected_CW_p_7', 'corrected_CW_p_11', 'corrected_CW_p_15']

txeq        = ['tx_ffe_cm2', 'tx_ffe_cm1', 'tx_ffe_c0', 'tx_ffe_cp1']

rxeq        = ['rx-eq_vga', 'rx-eq_ctle', 'rx-eq_mbz', 'rx-eq_iqclk', 'rx-eq_dfe_e_1', 'rx-eq_dfe_e_2', 'rx-eq_dfe_e_3', 'rx-eq_dfe_e_4', 'rx-eq_dfe_e_5',
                'rx-eq_dfe_e_6', 'rx-eq_dfe_e_7', 'rx-eq_dfe_e_8', 'rx-eq_dfe_e_9', 'rx-eq_dfe_e_10', 'rx-eq_dfe_e_11', 'rx-eq_dfe_e_12', 'rx-eq_dfe_e_13',
                'rx-eq_dfe_e_14', 'rx-eq_dfe_e_15', 'rx-eq_dfe_e_16', 'rx-eq_dfe_o_1', 'rx-eq_dfe_o_2', 'rx-eq_dfe_o_3', 'rx-eq_dfe_o_4', 'rx-eq_dfe_o_5',
                'rx-eq_dfe_o_6', 'rx-eq_dfe_o_7', 'rx-eq_dfe_o_8', 'rx-eq_dfe_o_9', 'rx-eq_dfe_o_10', 'rx-eq_dfe_o_11', 'rx-eq_dfe_o_12', 'rx-eq_dfe_o_13',
                'rx-eq_dfe_o_14', 'rx-eq_dfe_o_15', 'rx-eq_dfe_o_16']

ehm         = ['ehm_eye_0', 'ehm_eye_1', 'ehm_eye_2', 'min_EHM']

fec_calc    = ['total_sym_err_corr', 'fec_margin', 'RS_SER', 'RS_FLR']


class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, namednodes.registers.FieldValue):
            return str(o)
        return super().default(o)


def convert_dict_values_to_float(input_dict):
    output_dict = {}
    for key, value in input_dict.items():
        if is_numeric(value):
            output_dict[key] = float(value)
    return output_dict

def convert_to_json(fullpath, dict_results):
    with open(fullpath, 'w', encoding='utf-8') as json_file:
        json.dump(dict_results, json_file, cls=NpEncoder, indent=4)

def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def ehm_get(file_path):
    ehm_dict = {}
    for i in range(4):
        ehm_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('phy-ehm' in file_p[counter]):
            counter += 1
        for i in range(4):
            count_off = counter + 5 + 3*i
            if 'value' in file_p[count_off]:
                strlist = file_p[count_off].split(' ')
                while '' in strlist: strlist.remove('')
                for ind in range(3):
                    ehm_dict[i][ehm[ind]] = strlist[ind+1].strip()
    return (ehm_dict)


def rxeq_get(file_path):
    rxeq_dict = {}
    for i in range(4):
        rxeq_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('phy-rx-eq' in file_p[counter]):
            counter += 1
        for i in range(4):
            strlist2 = []
            for j in [0,3,4]:
                count_off = counter + 5 + j + 6*i
                strlist = file_p[count_off].strip().split(' ')
                while '' in strlist: strlist.remove('')
                strlist2 += strlist
            for var in strlist2:
                if not is_numeric(var):
                    strlist2.remove(var)
            for ind in range(len(rxeq)):
                rxeq_dict[i][rxeq[ind]] = strlist2[ind]
    return (rxeq_dict)

def txeq_get(file_path):
    txeq_dict = {}
    for i in range(4):
        txeq_dict[i] = {}
    counter = 0
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('phy-tx-eq-current' in file_p[counter]):
            counter += 1
        for i in range(4):
            strlist = file_p[counter].strip().split(' ')
            while '' in strlist: strlist.remove('')
            for ind in range(len(txeq)):
                txeq_dict[i][txeq[ind]] = strlist[1 + ind + 4*i]
    return (txeq_dict)



def fec_det_get(file_path):
    fec_dict = {}
    for i in range(4):
        fec_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('Total CW received' in file_p[counter]):
            counter += 1
        for i in range(4):
            strlist2 = []
            for j in [1,5,6,7,8]:
                count_off = counter + j + 12*i
                strlist = file_p[count_off].strip().split(' ')
                while '' in strlist: strlist.remove('')
                while '|' in strlist: strlist.remove('|')
                strlist2 += strlist
            for var in strlist2:
                if not is_numeric(var):
                    strlist2.remove(var)
            for ind in range(len(fec_det)):
                fec_dict[i][fec_det[ind]] = strlist2[ind +1]
    return(fec_dict)


def anlt_get(file_path):
    anlt_dict = {}
    for i in range(4):
        anlt_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('Port | AN retries raw' in file_p[counter]):
            counter += 1
        for i in range(4):
            count_off = counter + 2 + 6*i
            strlist = file_p[count_off].strip().split('|')
            while '' in strlist: strlist.remove('')
            for ind in range(len(ttl)):
                anlt_dict[i][ttl[ind]] = strlist[ind + 1].strip()
    return (anlt_dict)

def link_fault_get(file_path):
    Lf_dict = {}
    for i in range(4):
        Lf_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('show port attribute 0..7 link-fault-counters' in file_p[counter]):
            counter += 1
        for i in range(4):
            count_off = counter + 3
            strlist = file_p[count_off].strip().split(' ')
            while '' in strlist: strlist.remove('')
            strlist = strlist[1:]
            for var in strlist:
                if not is_numeric(var):
                    strlist.remove(var)
            for ind in range(len(link_faults)):
                Lf_dict[i][link_faults[ind]] = strlist[ind + i*3 ].strip()
    return (Lf_dict)


def attribute_get(file_path):
    attr_dict = {}
    for i in range(4):
        attr_dict[i] = {}
    with open(file_path, 'r') as file:
        for line in file:
            if any(element in line for element in attributes):
                line2 = line.split(' ')[0]
                if any(element == line2 for element in attributes):
                    strlist = line.split(' ')
                    while '' in strlist: strlist.remove('')
                    for i in range(4):
                        attr_dict[i][strlist[0]] = strlist[i+1]
    return (attr_dict)

def state_get(file_path):
    state_dict = {}
    for i in range(4):
        state_dict[i] = {}
    counter = 0
    with open(file_path, 'r') as file:
        file_p = file.readlines()
        while not ('show port 0..7  extended' in file_p[counter]):
            counter += 1
        for i in range(4):
            count_off = counter + 4 + i
            strlist = file_p[count_off].strip().split(' ')
            while '' in strlist: strlist.remove('')
            for ind in range(len(state)):
                state_dict[i][state[ind]] = strlist[ind +1]
    return(state_dict)


def metadata_get(file_path, protocol, targ_rate):
    ret_dict = init_params
    ret_dict['Metadata'] = {}
    ret_dict['Metadata']['Target_DataRate'] = targ_rate
    ret_dict['Metadata']['Protocol'] = protocol
    with open(file_path, 'r') as file:
        for line in file:
            if any(element in line for element in metadata):
                line2 = line.split(':')
                ret_dict['Metadata'][line2[0].strip()] = line2[1].strip()
    return(ret_dict)

def post_fec(fec_di, targ_rate):
    for i in range(4):
        rs_fec_total_cw = int(fec_di[i]['T_CW_received'])
        rs_fec_sym_err_corr = 0
        nCorr_symb = 0
        for j in range(1,16):
            rs_fec_sym_err_corr += int(fec_di[i]['corrected_CW_p_{}'.format(j)]) * j
            reg = int(fec_di[i]['corrected_CW_p_{}'.format(j)])
            if reg > 0:
                nCorr_symb = i
        fec_di[i]['total_sym_err_corr'] = rs_fec_sym_err_corr
        rs_fec_total_uncorr_cw = int(fec_di[i]['T_CW_uncorrected'])
        if rs_fec_total_cw != 0:
            if targ_rate ==  '50G' : #PAM4
                fec_di[i]['fec_margin']         = 15 - nCorr_symb
                fec_di[i]['RS_SER']             = float(rs_fec_sym_err_corr / (rs_fec_total_cw * 544))
            elif targ_rate ==  '25G' : #NRZ
                fec_di[i]['fec_margin']         = 7 - nCorr_symb
                fec_di[i]['RS_SER']             = float(rs_fec_sym_err_corr / (rs_fec_total_cw * 528))
            fec_di[i]['RS_FLR']                 = float(rs_fec_total_uncorr_cw / rs_fec_total_cw)
    return (fec_di)

def post_ehm(ehm_di, targ_rate):
    for i in range(4):
        if targ_rate ==  '50G' : #PAM4
            ehm_di[i]['min_EHM']         = min(int(ehm_di[i]['ehm_eye_0']),int(ehm_di[i]['ehm_eye_1']),int(ehm_di[i]['ehm_eye_2']))
        elif targ_rate ==  '25G' :
            ehm_di[i]['min_EHM']         = ehm_di[i]['ehm_eye_0']
        elif targ_rate ==  '10G' :
            ehm_di[i]['min_EHM']         = ehm_di[i]['ehm_eye_0']
    return (ehm_di)

def remap(state_dict,attr_dict,link_f_dict,anlt_dict,txeq_dict,rxeq_dict,fec_det_dict,ehm_dict):
    data_dict = {}
    for i in range(4):
        data_dict[i] = {}
        data_dict[i].update(convert_dict_values_to_float(state_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(attr_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(link_f_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(anlt_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(txeq_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(rxeq_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(fec_det_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(ehm_dict[i]))
    return (data_dict)

def remap10(state_dict,attr_dict,link_f_dict,anlt_dict,txeq_dict,rxeq_dict,ehm_dict):
    data_dict = {}
    for i in range(4):
        data_dict[i] = {}
        data_dict[i].update(convert_dict_values_to_float(state_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(attr_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(link_f_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(anlt_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(txeq_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(rxeq_dict[i]))
        data_dict[i].update(convert_dict_values_to_float(ehm_dict[i]))
    return (data_dict)


def list_dicts(first_dict,data_dict):
    mainlist = ['Mode', 'State', 'Speed', 'phy-fec-mode', 'phy-type-current', 'phy-lt-enable', 'phy-lt-options', 'phy-vsr-enable', 'phy-channel-type', 'phy-link-up-debouncing',
    'NF', 'LF', 'RF', 'AN retries', 'LT dur (ms)', 'Link Up (ms)', 'tx_ffe_cm2', 'tx_ffe_cm1', 'tx_ffe_c0', 'tx_ffe_cp1', 'rx-eq_vga', 'rx-eq_ctle', 'rx-eq_mbz',
    'rx-eq_iqclk', 'rx-eq_dfe_e_1', 'rx-eq_dfe_e_2', 'rx-eq_dfe_e_3', 'rx-eq_dfe_e_4', 'rx-eq_dfe_e_5', 'rx-eq_dfe_e_6', 'rx-eq_dfe_e_7', 'rx-eq_dfe_e_8', 'rx-eq_dfe_e_9',
    'rx-eq_dfe_e_10', 'rx-eq_dfe_e_11', 'rx-eq_dfe_e_12', 'rx-eq_dfe_e_13', 'rx-eq_dfe_e_14', 'rx-eq_dfe_e_15', 'rx-eq_dfe_e_16', 'rx-eq_dfe_o_1', 'rx-eq_dfe_o_2',
    'rx-eq_dfe_o_3', 'rx-eq_dfe_o_4', 'rx-eq_dfe_o_5', 'rx-eq_dfe_o_6', 'rx-eq_dfe_o_7', 'rx-eq_dfe_o_8', 'rx-eq_dfe_o_9', 'rx-eq_dfe_o_10', 'rx-eq_dfe_o_11',
    'rx-eq_dfe_o_12', 'rx-eq_dfe_o_13', 'rx-eq_dfe_o_14', 'rx-eq_dfe_o_15', 'rx-eq_dfe_o_16', 'ehm_eye_0', 'ehm_eye_1', 'ehm_eye_2', 'min_EHM',
    'T_CW_received', 'T_CW_corrected', 'T_CW_uncorrected', 'corrected_CW_p_0', 'corrected_CW_p_4', 'corrected_CW_p_8', 'corrected_CW_p_12', 'corrected_CW_p_1', 'corrected_CW_p_5',
    'corrected_CW_p_9', 'corrected_CW_p_13', 'corrected_CW_p_2', 'corrected_CW_p_6', 'corrected_CW_p_10', 'corrected_CW_p_14', 'corrected_CW_p_3', 'corrected_CW_p_7',
    'corrected_CW_p_11', 'corrected_CW_p_15', "total_sym_err_corr","fec_margin","RS_SER","RS_FLR"]
    Main_params = []
    Debug_params = []
    for i in range(4):
        main_dict = {'Lane' : i }
        debug_dict = {'Lane' : i }
        for var in data_dict[i].keys():
            if var in mainlist:
                main_dict[var]  = data_dict[i][var]
            else:
                debug_dict[var]  = data_dict[i][var]
        Main_params.append(main_dict)
        Debug_params.append(debug_dict)
    first_dict['Main_params']   = Main_params
    first_dict['Debug_params']  = Debug_params
    return (first_dict)


def parse_ppvfile(file_path, protocol, targ_rate, res_file):
    #====PROTOCOL SPEED CONFIG NAMING====
    if protocol == "10G-SFI":
        init_params['IP']='ETH_10G'
    elif protocol == "25GBase-CR":
        init_params['IP']='ETH_25G'
    else:
        init_params['IP']='ETH_50G'
    #====PROTOCOL SPEED CONFIG NAMING====
    first_dict      = metadata_get(file_path, protocol, targ_rate)
    state_dict      = state_get(file_path)
    attr_dict       = attribute_get(file_path)
    link_f_dict     = link_fault_get(file_path)
    txeq_dict       = txeq_get(file_path)
    rxeq_dict       = rxeq_get(file_path)
    anlt_dict       = anlt_get(file_path)
    if targ_rate == '10G':
        ehm_dict        = ehm_get(file_path)
        ehm_dict        = post_ehm(ehm_dict, targ_rate)
        data_dict       = remap10(state_dict,attr_dict,link_f_dict,anlt_dict,txeq_dict,rxeq_dict,ehm_dict)
        last_dict       = list_dicts(first_dict,data_dict)
    else:
        fec_det_dict    = fec_det_get(file_path)
        fec_det_dict    = post_fec(fec_det_dict, targ_rate)
        ehm_dict        = ehm_get(file_path)
        ehm_dict        = post_ehm(ehm_dict, targ_rate)
        data_dict       = remap(state_dict,attr_dict,link_f_dict,anlt_dict,txeq_dict,rxeq_dict,fec_det_dict,ehm_dict)
        last_dict       = list_dicts(first_dict,data_dict)

    convert_to_json(res_file, last_dict)
    # return res_file


def main(logpath,Eth_protocol,speed,res_path):

    # parse_ppvfile(r'C:\work\GRR\ppv\EHM_port_status_50G.txt', '50G_CR', '50G', r'C:\work\GRR\ppv\test_redo.json')
    # LocalTime = time.localtime()
    # Date = "{0:02d}_{1:02d}_{2:02d}".format(LocalTime[1], LocalTime[2], LocalTime[0])
    # Time = "{0:02d}_{1:02d}_{2:02d}".format(LocalTime[3], LocalTime[4], LocalTime[5])
    result_file = "{0}\GRR_Eth_Analog_Content_{1}.json".format(res_path,Eth_protocol)
    # result_file = "{0}\GRR_Eth_Analog_Content_{1}_{2}_{3}.json".format(res_path,Eth_protocol,Date,Time)
    parse_ppvfile(logpath,Eth_protocol,speed,result_file)
    return result_file

if __name__ == '__main__':
    main()