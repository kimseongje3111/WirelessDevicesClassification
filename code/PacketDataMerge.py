import classificationWirelessDevices.EachMerge as EachMerge
import pyshark
from collections import Counter


# Convert packets to probe requests.
# Integrate 3 Packet files by removing duplication.

def extrac_src(mininmum_PR, file_1, file_2, file_3):
    pb_filter = '(wlan.fc.type_subtype == 4)'
    packets_1 = pyshark.FileCapture(file_1, display_filter=pb_filter)
    packets_2 = pyshark.FileCapture(file_2, display_filter=pb_filter)
    packets_3 = pyshark.FileCapture(file_3, display_filter=pb_filter)

    wlan1_mac_list = [i.wlan.sa for i in packets_1]
    wlan2_mac_list = [i.wlan.sa for i in packets_2]
    wlan3_mac_list = [i.wlan.sa for i in packets_3]

    all_mac_list = wlan1_mac_list[:]
    all_mac_list.extend(wlan2_mac_list)
    all_mac_list.extend(wlan3_mac_list)

    all_count_dict = Counter(all_mac_list)
    wlan1_conunt_dict = Counter(wlan1_mac_list)
    wlan2_conunt_dict = Counter(wlan2_mac_list)
    wlan3_conunt_dict = Counter(wlan3_mac_list)

    master_mac_list = []
    for key in all_count_dict:
        if all_count_dict[key] >= mininmum_PR:
            if wlan1_conunt_dict[key] > 0 and wlan2_conunt_dict[key] > 0 and wlan3_conunt_dict[key] > 0:
                master_mac_list.append(key)

    packets_1.close()
    packets_2.close()
    packets_3.close()

    return master_mac_list


def every_src(mininmum_PR, file_list):
    pb_filter = '(wlan.fc.type_subtype == 4)'
    packets_1 = pyshark.FileCapture(file_list[0], display_filter=pb_filter)
    packets_2 = pyshark.FileCapture(file_list[1], display_filter=pb_filter)
    packets_3 = pyshark.FileCapture(file_list[2], display_filter=pb_filter)

    wlan1_mac_list = [i.wlan.sa for i in packets_1]
    print('# NIC_1\'s Probe Request Packet : ', len(wlan1_mac_list))

    wlan2_mac_list = [i.wlan.sa for i in packets_2]
    print('# NIC_2\'s Probe Request Packet : ', len(wlan2_mac_list))

    wlan3_mac_list = [i.wlan.sa for i in packets_3]
    print('# NIC_3\'s Probe Request Packet : ', len(wlan3_mac_list), '\n')

    all_mac_list = wlan1_mac_list[:]
    all_mac_list.extend(wlan2_mac_list)
    all_mac_list.extend(wlan3_mac_list)

    all_count_dict = Counter(all_mac_list)
    wlan1_count_dict = Counter(wlan1_mac_list)
    wlan2_count_dict = Counter(wlan2_mac_list)
    wlan3_count_dict = Counter(wlan3_mac_list)

    master_mac_list = []
    for key in all_count_dict:
        if all_count_dict[key] >= mininmum_PR:
            if wlan1_count_dict[key] > 0 and wlan2_count_dict[key] > 0 and wlan3_count_dict[key] > 0:
                tmp_count_list = [wlan1_count_dict[key], wlan2_count_dict[key], wlan3_count_dict[key]]
                master_mac_list.append([key, tmp_count_list])

    packets_1.close()
    packets_2.close()
    packets_3.close()

    print('# Device : ', len(master_mac_list))
    print('--------------------------------------------------------------')

    return master_mac_list


def start_merge(mininmum_PR, file1, file2, file3):
    file_list = [file1, file2, file3]
    master_list = []
    mac_list = []

    src_list = every_src(mininmum_PR, file_list)

    for mac, count_list in src_list:
        print('>> [' + str(len(mac_list) + 1) + '/' + str(len(src_list)) + '] Target Device :', mac, '\n')
        mac_list.append(mac)

        for i in range(3):
            print('# NIC_' + str(i + 1) + '\'s Target device\'s Packet : ', count_list[i])

        tmp_merged = EachMerge.main(file_list, mac, count_list)

        print('\n# Merged Packet :', len(tmp_merged))
        master_list.append(tmp_merged)
        del tmp_merged

        print('--------------------------------------------------------------')

    return master_list, mac_list
