import classificationWirelessDevices.PacketDataMerge as Packet
import classificationWirelessDevices.Feature as Feature
import classificationWirelessDevices.Classification as Classification
import classificationWirelessDevices.Performance as Performance

samplePacket = ["./data/191018_wlan1.pcapng",
                "./data/191018_wlan2.pcapng",
                "./data/191018_wlan3.pcapng"]


def Main():
    print(">> Start System\n")
    print('==============================================================\n')

    # Packet
    print("... Start merging packets ...\n")
    print('==============================================================')
    mergedPacket, src_list = Packet.start_merge(200, samplePacket[0], samplePacket[1], samplePacket[2])

    # Feature
    print('\n==============================================================\n')
    print("... Start creating feature ...\n")
    print('==============================================================')
    Feature.createFeatureFromInterBurstLatency(src_list, mergedPacket)

    # Classification
    print('==============================================================\n')
    print("... Start classification ...\n")
    print('==============================================================')
    classificationModel, tstx, tsty = Classification.createClassificationModel()

    # Performance
    print('==============================================================\n')
    print("... Start evaluating performance ...\n")
    print('==============================================================')
    Performance.evaluatePerformanceOfmodel(classificationModel, tstx, tsty)

    print('==============================================================\n')
    print(">> End System")


if __name__ == '__main__':
    Main()
