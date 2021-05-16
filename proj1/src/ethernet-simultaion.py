#!/usr/bin/python3

import random
import simpy
import math
import csv
import copy
import sys

import random


class BackOffImpl:

    def get(tag):
        if tag == "pp":
            return PPersistentBackOff(0.5)
        if tag == "op":
            return PPersistentBackOff(1/30)
        if tag == "beb":
            return BinaryExpBackOff()
        if tag == "lb":
            return LinearBackOff()
        return None

    def __str__(self):
        return "BackOffImpl"

    def notify_collision(self):
        pass

    def is_done(self):
        pass


class PPersistentBackOff(BackOffImpl):
    def __str__(self):
        return "PPersistentBackOff(p={:.3f})".format(self.p)

    def __init__(self, p):
        self.p = p

    def is_done(self):
        return random.uniform(0, 1) < self.p

    def notify_collision(self):
        pass


class BinaryExpBackOff(BackOffImpl):
    def __str__(self):
        return "BinaryExpBackOff"

    def __init__(self):
        self.wait_time = 0
        self.n = 0

    def notify_collision(self):
        self.n += 1
        self.wait_time = random.randrange((1 << min(self.n, 10)) + 1)

    def is_done(self):
        if self.wait_time < 0:
            return True
        else:
            self.wait_time -= 1
            return False


class LinearBackOff(BackOffImpl):
    def __str__(self):
        return "LinearBackOff"

    def __init__(self):
        self.wait_time = 0
        self.n = 0

    def notify_collision(self):
        self.n += 1
        self.wait_time = random.randrange(min(self.n, 1024) + 1)

    def is_done(self):
        if self.wait_time <= 0:
            return True
        else:
            self.wait_time -= 1
            return False


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


def simulate(back_off_impl, arrival_rate):
    env = simpy.Environment()
    stations = [StationProcess(env, i, arrival_rate, copy.deepcopy(back_off_impl))
                for i in range(G.STATION_NUM)]
    channel = ChannelProcess(env, stations)
    env.run(until=G.SIM_TIME)
    throughput = channel.sent_num / G.SIM_TIME
    print("Backoff: {}, lambda: {:.3f}, throughput: {:.2f}".format(
        back_off_impl, arrival_rate, throughput))
    return throughput


def simulate_all():
    back_off_impls = [PPersistentBackOff(0.5),
                      PPersistentBackOff(1/30),
                      BinaryExpBackOff(),
                      LinearBackOff()
                      ]
    for back_off_impl in back_off_impls:
        csv_name = '../plots/{}.csv'.format(back_off_impl)
        with open(csv_name, 'w', newline='') as csv_file:
            csv_writer = csv.DictWriter(
                csv_file, fieldnames=["lambda", "throughput"])
            csv_writer.writeheader()

            for arrival_rate in [.003 + a * .003 for a in range(10)]:
                throughput = simulate(
                    back_off_impl, arrival_rate)
                csv_writer.writerow(
                    {"lambda": arrival_rate, "throughput": throughput})


def help_msg(err):
    print(err)
    print("Usage: {} <tag> <lambda>".format(argv[0]))
    print("  <tag>: \"pp\", \"op\", \"beb\", or \"lb\" for four different back off algorithms.")
    print("  <lambda>: arrival rate, must be a float.")
    exit()


def main(argc, argv):
    random.seed(G.RANDOM_SEED)
    if argc <= 1:
        print("No argument provided, simulating all conditions.")
        simulate_all()
    else:
        if argc != 3:
            help_msg("Not enough arg provided.")
        back_off_impl = BackOffImpl.get(argv[1])
        if back_off_impl == None:
            help_msg("Error tag given")
        try:
            float(argv[2])
        except ValueError:
            help_msg("Arrival rate is not a float")
        print("Running one simnulation... ")
        simulate(back_off_impl, float(argv[2]))


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
