#!/usr/bin/python3

import random
import simpy
import math
import csv
import copy

from back_off import *


class G:
    RANDOM_SEED = 33
    T_S = 1
    STATION_NUM = 30
    SIM_TIME = 100000


class ChannelProcess(object):
    def __init__(self, env, stations):
        self.env = env
        self.stations = stations
        self.sent_num = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            senders = []
            for station in self.stations:
                if station.do_send():
                    senders.append(station)

            '''
            print("Time: {}.".format(self.env.now), end=" ")
            if len(senders) != 0:
                for sender in senders:
                    print("{}".format(sender.id), end=" ")
                print(" sending.")
            else:
                print()
            '''

            if len(senders) == 1:
                _ = senders[0].pkt_sent()
                self.sent_num += 1
            elif len(senders) > 1:
                for sender in senders:
                    sender.notify_collision()
            yield self.env.timeout(G.T_S)


class StationProcess(object):
    def __init__(self, env, id, arrival_rate, back_off_impl):

        self.env = env
        self.id = id
        self.arrival_rate = arrival_rate
        self.queue = []
        self.packet_number = 0
        self.collision = False
        self.back_off_impl = back_off_impl
        self.action = env.process(self.run())

    def run(self):
        while True:
            # Infinite loop for generating packets
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            # create and enque new packet
            self.packet_number += 1
            arrival_time = self.env.now
            new_packet = Packet(self.packet_number, arrival_time)
            self.queue.append(new_packet)

    def do_send(self):
        if self.collision:
            return self.back_off_impl.is_done()
        else:
            return len(self.queue) > 0

    def notify_collision(self):
        self.back_off_impl.notify_collision()
        self.collision = True

    def pkt_sent(self):
        self.collision = False
        return self.queue.pop(0)


class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


def main():
    random.seed(G.RANDOM_SEED)
    back_off_impls = [PPersistentBackOff(.5), PPersistentBackOff(
        1/G.STATION_NUM), BinaryExpBackOff(), LinearBackOff()]
    for back_off in back_off_impls:
        csv_name = '../plots/{}.csv'.format(back_off)
        with open(csv_name, 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file, fieldnames=["lambda", "throughput"])
            csv_writer.writeheader()

            for arrival_rate in [a / 1000 for a in range(1, 100)]:
                env = simpy.Environment()
                stations = [StationProcess(env, i, arrival_rate, copy.deepcopy(back_off))
                            for i in range(G.STATION_NUM)]
                channel = ChannelProcess(env, stations)
                env.run(until=G.SIM_TIME)
                throughput = channel.sent_num / G.SIM_TIME
                print("Backoff: {}, lambda: {}, throughput: {:.5f}".format(
                    back_off, arrival_rate, throughput))
                csv_writer.writerow(
                    {"lambda": arrival_rate, "throughput": throughput})


if __name__ == "__main__":
    main()
