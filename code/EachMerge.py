import operator
import pyshark
import datetime
from collections import OrderedDict


# ---------- 함수 선언 ----------

# 각 wlan들의 현재 index의 시간을 돌려줌 - 패킷 0개일때 불가
def every_wlan_time(wlan1_time_index, wlan2_time_index, wlan3_time_index):
    global standard_time

    wlan1_time = standard_time.replace(hour=int(wlan1packets[wlan1_time_index].frame_info.time[13:15]),
                                       minute=int(wlan1packets[wlan1_time_index].frame_info.time[16:18]),
                                       second=int(wlan1packets[wlan1_time_index].frame_info.time[19:21]))

    wlan2_time = standard_time.replace(hour=int(wlan2packets[wlan2_time_index].frame_info.time[13:15]),
                                       minute=int(wlan2packets[wlan2_time_index].frame_info.time[16:18]),
                                       second=int(wlan2packets[wlan2_time_index].frame_info.time[19:21]))

    wlan3_time = standard_time.replace(hour=int(wlan3packets[wlan3_time_index].frame_info.time[13:15]),
                                       minute=int(wlan3packets[wlan3_time_index].frame_info.time[16:18]),
                                       second=int(wlan3packets[wlan3_time_index].frame_info.time[19:21]))

    return wlan1_time, wlan2_time, wlan3_time


# 하나의 wlan의 시간만 알려줌
def each_time(wlan_num, time_index):
    global standard_time

    if wlan_num == 1:
        wlan_time = standard_time.replace(hour=int(wlan1packets[time_index].frame_info.time[13:15]),
                                          minute=int(wlan1packets[time_index].frame_info.time[16:18]),
                                          second=int(wlan1packets[time_index].frame_info.time[19:21]))
    elif wlan_num == 2:
        wlan_time = standard_time.replace(hour=int(wlan2packets[time_index].frame_info.time[13:15]),
                                          minute=int(wlan2packets[time_index].frame_info.time[16:18]),
                                          second=int(wlan2packets[time_index].frame_info.time[19:21]))

    else:
        wlan_time = standard_time.replace(hour=int(wlan3packets[time_index].frame_info.time[13:15]),
                                          minute=int(wlan3packets[time_index].frame_info.time[16:18]),
                                          second=int(wlan3packets[time_index].frame_info.time[19:21]))

    return wlan_time


# 기준시간과 같은 시간의 패킷들만 dict로 추출
def extract_sec_packet_dict():
    global sec
    global wlan1Index
    global wlan2Index
    global wlan3Index
    global wlan1_len
    global wlan2_len
    global wlan3_len
    global standard_time

    wlan1_tmp_dict = {}
    wlan2_tmp_dict = {}
    wlan3_tmp_dict = {}

    # wlan1
    for i in range(wlan1Index[0], wlan1_len):
        wlan1_time = each_time(1, wlan1Index[0])
        if wlan1_time == standard_time:
            wlan1_tmp_dict[wlan1packets[i].wlan.seq] = wlan1packets[i]
            wlan1Index[0] += 1
        else:
            break

    # wlan2
    for i in range(wlan2Index[0], wlan2_len):
        wlan2_time = each_time(2, wlan2Index[0])
        if wlan2_time == standard_time:
            wlan2_tmp_dict[wlan2packets[i].wlan.seq] = wlan2packets[i]
            wlan2Index[0] += 1
        else:
            break

    # wlan3
    for i in range(wlan3Index[0], wlan3_len):
        wlan3_time = each_time(3, wlan3Index[0])
        if wlan3_time == standard_time:
            wlan3_tmp_dict[wlan3packets[i].wlan.seq] = wlan3packets[i]
            wlan3Index[0] += 1
        else:
            break

    return wlan1_tmp_dict, wlan2_tmp_dict, wlan3_tmp_dict


# 두개의 dict 머지
def merge_tmp_dic(dict1, dict2):
    dict2.update(dict1)
    sortTmpDict = sorted(dict2.items(), key=operator.itemgetter(0))
    orderTmpDict = OrderedDict(sortTmpDict)
    ordered_dict = orderTmpDict

    return ordered_dict


def find_min_time(time_list):
    if time_list[0] != 0 and time_list[1] != 0 and time_list[2] != 0:
        min_time = min(time_list[0], time_list[1], time_list[2])
    elif time_list[0] != 0 and time_list[1] != 0 and time_list[2] == 0:
        min_time = min(time_list[0], time_list[1])
    elif time_list[0] != 0 and time_list[1] == 0 and time_list[2] != 0:
        min_time = min(time_list[0], time_list[2])
    elif time_list[0] == 0 and time_list[1] != 0 and time_list[2] != 0:
        min_time = min(time_list[1], time_list[2])
    elif time_list[0] != 0 and time_list[1] == 0 and time_list[2] == 0:
        min_time = time_list[0]
    elif time_list[0] == 0 and time_list[1] != 0 and time_list[2] == 0:
        min_time = time_list[1]
    elif time_list[0] == 0 and time_list[1] == 0 and time_list[2] != 0:
        min_time = time_list[2]
    else:
        min_time = 0

    return min_time


def extract_src_master():
    global standard_time

    standard_time = find_min_time(every_wlan_time(0, 0, 0))

    if standard_time == 0:
        return 0

    master_merged_list = []
    sec_merged_list = []

    wlan1_tmp_dict, wlan2_tmp_dict, wlan3_tmp_dict = extract_sec_packet_dict()

    while True:
        if wlan1_tmp_dict and wlan2_tmp_dict and wlan3_tmp_dict:  # T T T
            tmp_ttt_dict = merge_tmp_dic(wlan2_tmp_dict, wlan3_tmp_dict)
            sec_merged_list = list(merge_tmp_dic(wlan1_tmp_dict, tmp_ttt_dict).values())

        elif wlan1_tmp_dict and wlan2_tmp_dict and not wlan3_tmp_dict:  # T T F
            sec_merged_list = list(merge_tmp_dic(wlan1_tmp_dict, wlan2_tmp_dict).values())

        elif wlan1_tmp_dict and not wlan2_tmp_dict and wlan3_tmp_dict:  # T F T
            sec_merged_list = list(merge_tmp_dic(wlan1_tmp_dict, wlan3_tmp_dict).values())

        elif wlan1_tmp_dict and not wlan2_tmp_dict and not wlan3_tmp_dict:  # T F F
            sec_merged_list = list(wlan1_tmp_dict.values())

        elif not wlan1_tmp_dict and wlan2_tmp_dict and wlan3_tmp_dict:  # F T T
            sec_merged_list = list(merge_tmp_dic(wlan2_tmp_dict, wlan3_tmp_dict).values())

        elif not wlan1_tmp_dict and wlan2_tmp_dict and not wlan3_tmp_dict:  # F T F
            sec_merged_list = list(wlan2_tmp_dict.values())

        elif not wlan1_tmp_dict and not wlan2_tmp_dict and wlan3_tmp_dict:  # F F T
            sec_merged_list = list(wlan3_tmp_dict.values())

        elif not wlan1_tmp_dict and not wlan2_tmp_dict and not wlan3_tmp_dict:  # F F F
            pass

        if sec_merged_list:
            master_merged_list += sec_merged_list
            del sec_merged_list[:]

        if wlan1_len == wlan1Index[0] and wlan2_len == wlan2Index[0] and wlan3_len == wlan3Index[0]:
            break

        tmp_min_time = min(every_wlan_time(wlan1Index[0], wlan2Index[0], wlan3Index[0]))
        if tmp_min_time > standard_time:
            standard_time = tmp_min_time
        else:
            standard_time = standard_time + time_delta

        wlan1_tmp_dict, wlan2_tmp_dict, wlan3_tmp_dict = extract_sec_packet_dict()

    return master_merged_list


def init_merge(src, each_count):
    # ---------- 변수 선언 ---------- #

    # 필터 명시
    probeRequest = '(wlan.fc.type_subtype == 4)'
    targetDeviceMac = '(wlan.sa == ' + src + ')'  # '(wlan.sa == 08:e6:89:f2:b8:b1)'
    displayFilter = probeRequest + '&&' + targetDeviceMac

    # 캡처 파일 로드 및 필터 적용
    global wlan1packets
    global wlan2packets
    global wlan3packets

    wlan1packets = pyshark.FileCapture(file_list[0], display_filter=displayFilter)
    wlan2packets = pyshark.FileCapture(file_list[1], display_filter=displayFilter)
    wlan3packets = pyshark.FileCapture(file_list[2], display_filter=displayFilter)

    # 각 wlan의 최대 패킷 수
    global wlan1_len
    global wlan2_len
    global wlan3_len

    wlan1_len = each_count[0] - 1
    wlan2_len = each_count[1] - 1
    wlan3_len = each_count[2] - 1

    # 각 AP의 현재 패킷 위치
    global wlan1Index
    global wlan2Index
    global wlan3Index

    wlan1Index = [0]
    wlan2Index = [0]
    wlan3Index = [0]

    # 시간 계산을 위한 변수
    global standard_time
    global time_delta

    standard_time = datetime.datetime.today()
    time_delta = datetime.timedelta(seconds=1)

    return extract_src_master()


def main(addr_list, src, count):
    global file_list
    file_list = addr_list
    last_merged = init_merge(src, count)
    wlan1packets.close()
    wlan2packets.close()
    wlan3packets.close()

    return last_merged
