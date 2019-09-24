#How to run: put wrapper.py in the same root file directory, then run it

import operator
import random
import sys
import time
seed = 1225
import random
from collections import defaultdict
import numpy
numpy.random.seed(seed)
def random_arrival(job_number, Lambda):
    Uk = numpy.random.uniform(0, 1, job_number)
    arrivalTime = -numpy.log(1-Uk)/Lambda
    for i in range(1, job_number):
        arrivalTime[i] = arrivalTime[i] + arrivalTime[i-1]
    return arrivalTime

def random_service(Beta, Alpha_1, Alpha_2, job_number):
    Prob = numpy.random.uniform(0, 1, job_number)
    gama = (1 - Beta) / ((Alpha_2 ** (1 - Beta)) - (Alpha_1 ** (1 - Beta)))
    service_time = (Prob * (1 - Beta) / gama + Alpha_1 ** (1 - Beta)) ** (1 / (1 - Beta))
    return service_time
def random_latency(v1, v2, job_number):
    latency_list = numpy.random.uniform(v1,v2,job_number)
    return latency_list
def master_exchange(preMaster, currentMaster, nextMaster):
    master_control_list = []
    master_control_list.append(preMaster)
    master_control_list.append(currentMaster)
    master_control_list.append(nextMaster)
    if len(master_control_list) == 3:
        preMaster, currentMaster = master_control_list[1], master_control_list[2]
        master_interval = master_control_list[2] - master_control_list[1]
    return preMaster, currentMaster, master_interval
def event_scope(nextInQue, nextFogPushed, nextCloudPush, nextNetPush ):
    nextMaster = min(nextInQue, nextFogPushed,  nextCloudPush, nextNetPush)
    if nextMaster == nextInQue:
        position = 1#system.queue
    elif nextMaster == nextFogPushed:
        position = 2#system.fog
    elif nextMaster == nextNetPush:
        position = 3#system.net
    elif nextMaster == nextCloudPush:
        position = 4#system.cloud
    switch = 1 if nextMaster < 99999999 else 0
    return switch, position, nextMaster

    #switch = 1 if nextMaster < 99999999 else 0
    #return switch, cost, nextMaster
def nextCreat():
    nextfog, nextnet, nextcloud = 0, 0, 0
    initList = []
    initList.append(nextfog)
    initList.append(nextnet)
    initList.append(nextcloud)
    for i in range(len(initList)):
        initList[i] = 99999
    return initList[0], initList[1], initList[2]





class Request:
    def __init__(self, jobOrder, fogArrival, serviceTime, netLatency):
        self.fogRemain, self.fogService ,self.jobOrder,  self.fogArrival, self.netLatency = serviceTime, serviceTime, jobOrder, fogArrival, netLatency
        self.fogPushed, self.netReceived, self.netPushed, self.cloudReceived, self.cloudPushed   = 99999, 99999,99999,99999,99999
        self.jobCloudProcessed, self.jobFinished, self.inLimit = False, False, True
        self.cloudRemain, self.jobRT = 0, 0
    #def initiatetime(self,a, b, c, d, e):
        #a, b, c, d, e = 99999, 99999, 99999, 99999, 99999
        #return a, b, c, d, e
class System:
    def __init__(self, components):
        self.queue,self.fog,self.net,self.cloud = 1, 2, 3, 4
        self.status = components
    def calssSpecification(self):
        print(self.status, "Components the system has")
def man(expected_num, arrival_list,service_list,network_latency_list,fogTimeLimit,TimeToCloud,time_end=99999999):
    currentMaster, preMaster, nextMaster = 0, 0, 0
    position = None
    reqList, fogList, netList, cloudList = [], [], [], []
    indexDict = {'nextArriving':0 ,'nextFogPushing':0, 'nextNetPushing':0, 'nextCloudPushing':0, 'fogDelivery':0}


    system = System(4)
    if not position:
        position = system.queue
    expected_job_number = len(arrival_list)
    start_job = 0
    while start_job < expected_job_number:

        reqList.append(Request(start_job, arrival_list[start_job], service_list[start_job], network_latency_list[start_job]))
        limit_flag = 1
        while reqList[start_job].fogService > fogTimeLimit and limit_flag == 1:
            reqList[start_job].inLimit = False
            limit_flag = 0
        start_job = start_job + 1
    # load the first job into the job_process_list
    if len(arrival_list) < 1:
        return
    elif len(arrival_list) >= 1:
        arrival_control_list = []
        arrival_control_list.append(reqList[indexDict['nextArriving']].fogArrival)
        arrival_control_list.append(reqList[indexDict['nextArriving']].jobFinished)
        nextInQue = arrival_control_list[0]
        if len(arrival_control_list) >= 1:
            nextMaster = arrival_control_list[0]

    open_case, switch = 1, 1
    print("time_end",time_end)
    while open_case == 1 and currentMaster < time_end:
        switch=0
        while position == system.queue:  # fog arrive event
            # 1. update fogList and clock
            nextFogPushed, nextNetPushed, nextCloudPushed = nextCreat()

            preMaster, currentMaster, master_interval = master_exchange(preMaster, currentMaster, nextMaster)

            for i in range(len(fogList)):
                reqList[fogList[i]].fogRemain = reqList[fogList[i]].fogRemain - master_interval / len(fogList)

            if not reqList:
                print("reqList is empty")
            else:
                fogList.append(reqList[indexDict['nextArriving']].jobOrder)  # we only store the job index in the list



            arrivalClock = 1
            while arrivalClock == 1:
                if indexDict['nextArriving'] < len(reqList) - 1:
                    indexDict['nextArriving'] = indexDict['nextArriving'] + 1
                    if not reqList:
                        print("There is no job")
                        indexDict['nextArriving'] = 0
                    else:
                        nextInQue = reqList[indexDict['nextArriving']].fogArrival
                else:
                    indexDict['nextArriving'] = indexDict['nextArriving'] + 1  # for following unifom use
                    nextInQue = 99999  # set a infinit value, so arrive event will never be choose as the next event
                arrivalClock = 0


            for i in range(len(fogList)):  # now the new arrive job in the list, choose the first next_depart job in the list
                reference_1 = fogTimeLimit - reqList[fogList[i]].fogService + reqList[fogList[i]].fogRemain
                reference_2 = reqList[fogList[i]].fogRemain
                if reference_1 * len(fogList) > reference_2 * len(fogList):
                    departureTime = reference_2 * len(fogList) + currentMaster
                if reference_1 * len(fogList) <= reference_2 * len(fogList):
                    departureTime = reference_1 * len(fogList) + currentMaster


                check_dep_list = []
                check_dep_list.append(nextFogPushed)
                check_dep_list.append(departureTime)
                if min(check_dep_list[0], check_dep_list[1]) == check_dep_list[1]:
                    nextFogPushed = departureTime
                    if not check_dep_list:
                        print("Error!")
                        return
                    else:
                        indexDict['nextFogPushing'] = fogList[i]




            # 2. update netList
            for i in range(len(netList)):
                reqList[netList[i]].netLatency = reqList[netList[i]].netLatency - master_interval

            for i in range(len(netList)):
                departureTime =  reqList[netList[i]].netLatency + currentMaster

                net_dep_list = []
                if not net_dep_list:
                    net_dep_list.append(nextNetPushed)
                    net_dep_list.append(departureTime)

                    if min(net_dep_list[0], net_dep_list[1]) == net_dep_list[1]:
                        nextNetPushed = departureTime
                        if not net_dep_list:
                            print("Error")
                        else:
                            indexDict['nextNetPushing'] = netList[i]



            # 3.update cloudList:

            for i in range(len(cloudList)):
                reqList[cloudList[i]].cloudRemain = reqList[cloudList[i]].cloudRemain - master_interval / len(cloudList)


            for i in range(len(cloudList)):  # choose the first next_depart job in the list
                departureTime = currentMaster + (reqList[cloudList[i]].cloudRemain * len(cloudList))
                cloud_dep_list = []
                if not cloud_dep_list:
                    cloud_dep_list.append(nextCloudPushed)
                    cloud_dep_list.append(departureTime)

                    if cloud_dep_list[0] > cloud_dep_list[1]:
                        nextCloudPushed = departureTime
                        if cloud_dep_list:
                            indexDict['nextCloudPushing'] = cloudList[i]





            # 4.update the next event min(next_arrive, next_fog_dep,next_net_dep,next_cloud_dep), update the event_flag to corresponding next event value.

            switch, position, nextMaster = event_scope(nextInQue, nextFogPushed, nextCloudPushed, nextNetPushed)
            #print(currentMaster)
            #break
        while position == system.fog:  # fog departure event
            # 0. update fogList and clock
            preMaster, currentMaster, master_interval = master_exchange(preMaster, currentMaster, nextMaster)
            nextFogPushed, nextNetPushed, nextCloudPushed = nextCreat()

            #   1.1--compute the fog_remain_service_time for each job
            for i in range(len(fogList)):
                reqList[fogList[i]].fogRemain = reqList[fogList[i]].fogRemain - master_interval / len(fogList)








            # 1.2--handle the departure job
            if fogList:
                if not reqList[indexDict['nextFogPushing']].inLimit:  # job completed:
                    reqList[indexDict['nextFogPushing']].fogPushed, reqList[indexDict['nextFogPushing']].netReceived = currentMaster, currentMaster
                    reqList[indexDict['nextFogPushing']].cloudRemain = reqList[indexDict['nextFogPushing']].fogRemain * TimeToCloud
                    fogList.remove(indexDict['nextFogPushing'])
                    fog_to_net, indexDict['fogDelivery'] = True, indexDict['nextFogPushing']

                    ###############################################################

                elif reqList[indexDict['nextFogPushing']].inLimit:  # job don't completed but reach the fogTimeLimit
                    reqList[indexDict['nextFogPushing']].fogPushed, reqList[indexDict['nextFogPushing']].jobFinished = currentMaster, True
                    judgement = operator.eq(reqList[indexDict['nextFogPushing']].fogPushed, currentMaster)
                    if judgement:
                        reqList[indexDict['nextFogPushing']].jobRT = reqList[
                                                                         indexDict['nextFogPushing']].fogPushed - \
                                                            reqList[indexDict['nextFogPushing']].fogArrival
                    fogList.remove(indexDict['nextFogPushing'])
                    fog_to_net = False
                    reqList[indexDict['nextFogPushing']].jobCloudProcessed = False
            else:
                print("No job in the Fog!")

            for i in range(len(fogList)):
                reference_1 = fogTimeLimit - reqList[fogList[i]].fogService + reqList[fogList[i]].fogRemain
                reference_2 = reqList[fogList[i]].fogRemain
                if reference_1 * len(fogList) > reference_2 * len(fogList):
                    departureTime = reference_2 * len(fogList) + currentMaster
                if reference_1 * len(fogList) <= reference_2 * len(fogList):
                    departureTime = reference_1 * len(fogList) + currentMaster

                check_dep_list = []
                check_dep_list.append(nextFogPushed)
                check_dep_list.append(departureTime)
                if min(check_dep_list[0], check_dep_list[1]) == check_dep_list[1]:
                    nextFogPushed = departureTime
                    if not check_dep_list:
                        print("Error!")
                        return
                    else:
                        indexDict['nextFogPushing'] = fogList[i]

            net_compared_list =  [0]
            for i in range(len(netList)):
                reqList[netList[i]].netLatency = reqList[netList[i]].netLatency - master_interval

            if net_compared_list:
                for i in range(len(net_compared_list)):
                    if fog_to_net:
                        netList.append(indexDict['fogDelivery'])
                        fog_to_net = False
                for i in range(len(netList)):
                    departureTime = reqList[netList[i]].netLatency + currentMaster

                    net_dep_list = []
                    if not net_dep_list:
                        net_dep_list.append(nextNetPushed)
                        net_dep_list.append(departureTime)
                        if min(net_dep_list[0], net_dep_list[1]) == net_dep_list[1]:
                            nextNetPushed = departureTime
                            if not net_dep_list:
                                print("Error")
                            else:
                                indexDict['nextNetPushing'] = netList[i]
            # 3.update cloudList:
            for i in range(len(cloudList)):
                reqList[cloudList[i]].cloudRemain = reqList[cloudList[i]].cloudRemain - master_interval / len(cloudList)


            for i in range(len(cloudList)):  # choose the first next_depart job in the list
                departureTime = currentMaster + (reqList[cloudList[i]].cloudRemain * len(cloudList))
                cloud_dep_list = []
                if not cloud_dep_list:
                    cloud_dep_list.append(nextCloudPushed)
                    cloud_dep_list.append(departureTime)
                    if min(cloud_dep_list[0], cloud_dep_list[1]) == cloud_dep_list[1]:
                        nextCloudPushed = departureTime
                        if cloud_dep_list:
                            indexDict['nextCloudPushing'] = cloudList[i]
            switch, position, nextMaster = event_scope(nextInQue, nextFogPushed, nextCloudPushed, nextNetPushed)
            #print(currentMaster)











        while position == system.net:  # net departure event
            # 0. update fogList and clock
            nextFogPushed, nextNetPushed, nextCloudPushed = nextCreat()
            preMaster, currentMaster, master_interval = master_exchange(preMaster, currentMaster, nextMaster)




            #   1.1--compute the fog_remain_service_time for each job
            for i in range(len(fogList)):
                reqList[fogList[i]].fogRemain = reqList[fogList[i]].fogRemain - master_interval / len(fogList)

            for i in range(len(fogList)):  # choose the first next_depart job in the list
                reference_1 = fogTimeLimit - reqList[fogList[i]].fogService + reqList[
                    fogList[i]].fogRemain
                reference_2 = reqList[fogList[i]].fogRemain
                if reference_1 * len(fogList) > reference_2 * len(fogList):
                    departureTime = reference_2 * len(fogList) + currentMaster
                if reference_1 * len(fogList) <= reference_2 * len(fogList):
                    departureTime = reference_1 * len(fogList) + currentMaster

                check_dep_list = []
                check_dep_list.append(nextFogPushed)
                check_dep_list.append(departureTime)
                if min(check_dep_list[0], check_dep_list[1]) == check_dep_list[1]:
                    nextFogPushed = departureTime
                    if not check_dep_list:
                        print("Error!")
                        return
                    else:
                        indexDict['nextFogPushing'] = fogList[i]


            for i in range(len(netList)):
                reqList[netList[i]].netLatency = reqList[netList[i]].netLatency - master_interval
            # net_to_cloud=True
            net_to_cloud_job_index, reqList[indexDict['nextNetPushing']].netPushed = indexDict['nextNetPushing'], currentMaster
            netList.remove(indexDict['nextNetPushing'])
            for i in range(len(netList)):
                departureTime = reqList[netList[i]].netLatency + currentMaster

                net_dep_list = []
                if not net_dep_list:
                    net_dep_list.append(nextNetPushed)
                    net_dep_list.append(departureTime)
                    if min(net_dep_list[0], net_dep_list[1]) == net_dep_list[1]:
                        nextNetPushed = departureTime
                        if not net_dep_list:
                            print("Error")
                        else:
                            indexDict['nextNetPushing'] = netList[i]


            # 3.update cloudList:
            for i in range(len(cloudList)):
                reqList[cloudList[i]].cloudRemain = reqList[cloudList[i]].cloudRemain - master_interval / len(cloudList)
            # if net_to_cloud==True:

            cloudList.append(net_to_cloud_job_index)
            reqList[net_to_cloud_job_index].cloudReceived = currentMaster
            # net_to_cloud=False

            for i in range(len(cloudList)):  # choose the first next_depart job in the list
                departureTime = (reqList[cloudList[i]].cloudRemain * len(cloudList)) + currentMaster
                cloud_dep_list = []
                if not cloud_dep_list:
                    cloud_dep_list.append(nextCloudPushed)
                    cloud_dep_list.append(departureTime)
                    if min(cloud_dep_list[0], cloud_dep_list[1]) == cloud_dep_list[1]:
                        nextCloudPushed = departureTime
                        if cloud_dep_list:
                            indexDict['nextCloudPushing'] = cloudList[i]
                else:
                    print("Error")

            switch, position, nextMaster = event_scope(nextInQue, nextFogPushed, nextCloudPushed, nextNetPushed)
            #print(currentMaster)







        while position == system.cloud:  # cloud departure event
            nextFogPushed, nextNetPushed, nextCloudPushed = nextCreat()
            # 0. update clock
            position = system.queue
            preMaster, currentMaster, master_interval = master_exchange(preMaster, currentMaster, nextMaster)

            #   1.1--compute the fog_remain_service_time for each job

            for i in range(len(fogList)):
                reqList[fogList[i]].fogRemain = reqList[fogList[i]].fogRemain - master_interval / len(fogList)
            for i in range(len(fogList)):
                reference_1 = fogTimeLimit - reqList[fogList[i]].fogService + reqList[
                    fogList[i]].fogRemain
                reference_2 = reqList[fogList[i]].fogRemain
                if reference_1 * len(fogList) > reference_2 * len(fogList):
                    departureTime = reference_2 * len(fogList) + currentMaster
                if reference_1 * len(fogList) <= reference_2 * len(fogList):
                    departureTime = reference_1 * len(fogList) + currentMaster

                check_dep_list = []
                check_dep_list.append(nextFogPushed)
                check_dep_list.append(departureTime)
                if min(check_dep_list[0], check_dep_list[1]) == check_dep_list[1]:
                    nextFogPushed = departureTime
                    if not check_dep_list:
                        print("Error!")
                        return
                    else:
                        indexDict['nextFogPushing'] = fogList[i]

            # 2. update netList
            #This part has been changed


            for i in range(len(netList)):
                reqList[netList[i]].netLatency = reqList[netList[i]].netLatency - master_interval
                departureTime = reqList[netList[i]].netLatency + currentMaster
                net_dep_list = []
                if not net_dep_list:
                    net_dep_list.append(nextNetPushed)
                    net_dep_list.append(departureTime)
                    if min(net_dep_list[0], net_dep_list[1]) == net_dep_list[1]:
                        nextNetPushed = departureTime
                        if not net_dep_list:
                            print("Error")
                        else:
                            indexDict['nextNetPushing'] = netList[i]

            # 3.update cloudList:
            for i in range(len(cloudList)):
                reqList[cloudList[i]].cloudRemain = reqList[cloudList[i]].cloudRemain - master_interval / len(cloudList)
            # 3.2--handle the departure job
                reqList[indexDict['nextCloudPushing']].jobFinished, reqList[indexDict['nextCloudPushing']].jobCloudProcessed, reqList[indexDict['nextCloudPushing']].cloudPushed = True, True, currentMaster
                reqList[indexDict['nextCloudPushing']].jobRT = reqList[indexDict['nextCloudPushing']].cloudPushed - \
                                                      reqList[indexDict['nextCloudPushing']].fogArrival
            cloudList.remove(indexDict['nextCloudPushing'])

            for i in range(len(cloudList)):  # choose the first next_depart job in the list
                departureTime = (reqList[cloudList[i]].cloudRemain * len(cloudList)) + currentMaster
                cloud_dep_list = []
                if not cloud_dep_list:
                    cloud_dep_list.append(nextCloudPushed)
                    cloud_dep_list.append(departureTime)
                    if min(cloud_dep_list[0], cloud_dep_list[1]) == cloud_dep_list[1]:
                        nextCloudPushed = departureTime
                        if cloud_dep_list:
                            indexDict['nextCloudPushing'] = cloudList[i]








            # 4.update the next event min(next_arrive, next_fog_dep,next_net_dep,next_cloud_dep), update the event_flag to corresponding next event value.
            nextMaster = nextInQue
            departure_list = []
            departure_list.append(nextFogPushed)
            departure_list.append(nextNetPushed)
            departure_list.append(nextCloudPushed)
            if departure_list:
                if min(nextMaster, departure_list[0]) == departure_list[0]:
                    nextMaster = departure_list[0]
                    position = system.fog
                if min(nextMaster, departure_list[1]) == departure_list[1]:
                    nextMaster = departure_list[1]
                    position = system.net
                if min(nextMaster, departure_list[2]) == departure_list[2]:
                    nextMaster = departure_list[2]
                    position = system.cloud
            if nextMaster < 99999:
                switch = 1
            elif nextMaster >= 99999:
                switch = 0
            #print(currentMaster)

            break
        stop_falg = 0
        stop_list = []
        stop_list.append(fogList)
        stop_list.append(netList)
        stop_list.append(cloudList)
        for e in stop_list:
            if e:
                stop_falg + 1
        if switch or stop_falg != 0:
            continue
        else:
            open_case = 0



    reT = 0
    if time_end == 99999999:
        for i in range(len(reqList)):
            reT = reT + reqList[i].jobRT
        mrt = round(reT / len(reqList), 4)
        print("hello world!")
        print(expected_num)
        print("parameter is :")
        print(mrt)
        print("the pro ject is end!")

        print("expected_num:", expected_num)
        mrt_file = "mrt_" + expected_num + ".txt"
        fog_file = "fog_dep_" + expected_num + ".txt"
        net_file = "net_dep_" + expected_num + ".txt"
        cloud_file = "cloud_dep_" + expected_num + ".txt"
        with open(mrt_file, 'w') as f:
            f.write('{}\n'.format(mrt))

        with open(fog_file, 'w') as f:
            for i in range(len(reqList)):
                # f.write('{}\t{}\n'.format(round(reqList[i].fog_arrival,4),round(reqList[i].f1og_departure,4)))
                f.write(str("%.4f" % reqList[i].fogArrival))
                f.write("\t")
                f.write(str("%.4f" % reqList[i].fogPushed))
                f.write("\n")
        with open(net_file, 'w') as f:
            for i in range(len(reqList)):
                if reqList[i].jobCloudProcessed == True:  # completed at cloud means this job handled by the net
                    # f.write('{}\t{}\n'.format(reqList[i].fog_arrival,round(reqList[i].n1et_departure,4)))
                    f.write(str("%.4f" % reqList[i].fogArrival))
                    f.write("\t")
                    f.write(str("%.4f" % reqList[i].netPushed))
                    f.write("\n")
        with open(cloud_file, 'w') as f:
            for i in range(len(reqList)):
                if reqList[i].jobCloudProcessed == True:
                    # f.write('{}\t{}\n'.format(reqList[i].fog_arrival,round(reqList[i].cloudPushed,4)))
                    f.write(str("%.4f" % reqList[i].fogArrival))
                    f.write("\t")
                    f.write(str("%.4f" % reqList[i].cloudPushed))
                    f.write("\n")
    else:
        num = 0
        for i in range(len(reqList)):
            if reqList[i].jobFinished ==True:
                reT = reT + reqList[i].jobRT
                num+=1
        mrt = round(reT /num, 4)
        print("parameter is :")
        print(mrt)
        print("the pro ject is end!")
        mrt_file, fog_file, net_file, cloud_file = "mrt_" + expected_num + ".txt","fog_dep_" + expected_num + ".txt","net_dep_" + expected_num + ".txt", "cloud_dep_" + expected_num + ".txt"
        with open(mrt_file, 'w') as f:
            f.write('{}\n'.format(mrt))

        with open(fog_file, 'w') as f:
            job_count = 0
            for i in range(len(reqList)):
                if reqList[i].jobFinished == True:
                    job_count += 1

                    # f.write('{}\t{}\n'.format(round(reqList[i].fog_arrival,4),round(reqList[i].f1og_departure,4)))
                    f.write(str("%.4f" % reqList[i].fogArrival))
                    f.write("\t")
                    f.write(str("%.4f" % reqList[i].fogPushed))
                    f.write("\n")
            print("fog_completed_jobs", job_count)
        with open(net_file, 'w') as f:
            job_count = 0
            for i in range(len(reqList)):
                if reqList[i].jobCloudProcessed == True:  # completed at cloud means this job handled by the net
                    job_count += 1
                    # f.write('{}\t{}\n'.format(reqList[i].fog_arrival,round(reqList[i].netPushed,4)))
                    f.write(str("%.4f" % reqList[i].fogArrival))
                    f.write("\t")
                    f.write(str("%.4f" % reqList[i].netPushed))
                    f.write("\n")
            print("job_completed_cloud,", job_count)

        with open(cloud_file, 'w') as f:
            for i in range(len(reqList)):
                if reqList[i].jobCloudProcessed == True:
                    # f.write('{}\t{}\n'.format(reqList[i].fog_arrival,round(reqList[i].cloudPushed,4)))
                    f.write(str("%.4f" % reqList[i].fogArrival))
                    f.write("\t")
                    if reqList[i].cloudPushed > 1000:
                        reqList[i].cloudPushed = 1000
                    f.write(str("%.4f" % reqList[i].cloudPushed))
                    f.write("\n")











    return reqList








if __name__ == '__main__':
    mode, fogTimeLimit, TimeToCloud, time_end, file_nums = 0, 0, 0, 0, 0
    with open("num_tests.txt", "r") as test_infomation:
        line = test_infomation.read()
        file_nums = int(line[0])
    for elements in range(1, file_nums + 1):
    #open_up_times, right_bound = 1, file_nums + 1
    #while open_up_times < right_bound:
        expected_num = str(elements)
        modes, paras, arrivals, services, networks = "mode_" + expected_num + ".txt", "para_" + expected_num + ".txt", "arrival_" + expected_num + ".txt", "service_" + expected_num + ".txt", "network_" + expected_num + ".txt"
        arrival_list, service_list, network_latency_list = [], [], []  # for trace mode, all arrival time contained in the arrival_file
        job_nums, Lambda, a1_random, a2_random, b_random, v1_random, v2_random = 0, 0, 0, 0, 0, 0, 0
        with open(modes, "r") as open_file:
            mode_type = open_file.read()
            mode_judge = operator.eq(mode_type, "trace")
            mode = 0 if mode_judge else 1
        with open(paras, "r") as open_file:
            parameters = open_file.readlines()
            fogTimeLimit, TimeToCloud = float(parameters[0]), float(parameters[1])
            if mode == 1:
                time_end = float(parameters[2])
                #print("fog_time_lime=", fogTimeLimit, " TimeToCloud=", TimeToCloud, "random end_time=", time_end)
            else:
                print("fogTimeLimit=", fogTimeLimit, " TimeToCloud=", TimeToCloud)



        with open(arrivals, "r") as open_file:
            arrival_para = open_file.readlines()
            job_nums = len(arrival_para)
            if mode == 1:
                Lambda = float(arrival_para[0])
                job_number = int(time_end/0.001)
                arrival_list = random_arrival(job_number, Lambda)
                #print(arrival_list)
            if mode == 0:  # for trace mode arrival_file include all of arrival times
                arrival_count = 0
                while arrival_count < job_nums:
                    arrival_list.append(float(arrival_para[arrival_count]))
                    arrival_count = arrival_count + 1
                #print("arrival_list", arrival_list)
            else:  # mode=1 random mode, arrival_file is the value of lambada
                Lambda = float(line[0])



        with open(services, "r") as open_file:
            service_para = open_file.readlines()
            if mode == 1:  # mode=1 random mode, arrival_file is the value of lambada
                Alpha_1, Alpha_2, Beta = float(service_para[0]),float(service_para[1]), float(service_para[2])
                job_number_service = int(time_end/0.001)
                service_list = random_service(Beta, Alpha_1, Alpha_2, job_number_service)
                #print("random a1=", a1_random, "random a2=", a2_random, "random b=", b_random)
            if mode == 0:  # for trace mode arrival_file include all of arrival times
                #for i in range(job_nums):
                service_count = 0
                while service_count < job_nums:
                    service_list.append(float(service_para[service_count]))
                    service_count = service_count + 1
        #print("service_list", service_list)



        with open(networks, "r") as open_file:
            network_para = open_file.readlines()
            if mode == 1:  # mode=1 random mode, arrival_file is the value of lambada
                v1, v2 = float(network_para[0]), float(network_para[1])
                job_number_latency = int(time_end/0.001)
                network_latency_list = random_latency(v1, v2, job_number_latency)
            if mode == 0:
                network_counts = 0
                while network_counts < job_nums:
                    network_latency_list.append(float(network_para[network_counts]))
                    network_counts = network_counts + 1
        #print("network_latency_list", network_latency_list)
        #print("random v1=", v1, "random v2=", v2)
        #open_up_times = open_up_times + 1
        if mode == 0:  # call trace mode simulation function
            man(expected_num, arrival_list, service_list, network_latency_list, fogTimeLimit, TimeToCloud, time_end=99999999)
            #log_list = man(expected_num, arrival_list, service_list, network_latency_list, fogTimeLimit, TimeToCloud, time_end=99999999)
        if mode == 1:
            man(expected_num, arrival_list, service_list, network_latency_list, fogTimeLimit, TimeToCloud,time_end)
            #plot_list = man(expected_num, arrival_list, service_list, network_latency_list, fogTimeLimit, TimeToCloud,time_end)

