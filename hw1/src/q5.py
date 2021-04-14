import random
import simpy
import math


# First  define some global variables
class G:
    RANDOM_SEED = 33
    SIM_TIME = 100000
    MU = 1
    LONG_SLEEP_TIMER = 1000000000


class Server_Process(object):
    def __init__(self, env, Server_Idle_Periods, Packet_Delay):
        self.env = env
        self.len = 0  # total number of packets in the system
        self.queue = []  # the buffer
        self.server_busy = False
        # this will the area
        self.prevous_time = 0
        self.sum_time_length = 0
        self.delay = 0
        self.start_idle_time = 0
        self.Server_Idle_Periods = Server_Idle_Periods
        self.Packet_Delay = Packet_Delay
        self.action = env.process(self.run())

    def run(self):
        # print("TX-process started")
        while True:
            try:
                yield self.env.timeout(G.LONG_SLEEP_TIMER)
            except simpy.Interrupt:
                while self.len > 0:
                    packet = self.queue.pop()
                    yield self.env.timeout(random.expovariate(G.MU))
                    self.delay = self.env.now - packet.arrival_time
                    self.Packet_Delay.addNumber(self.delay)
                    self.sum_time_length += (self.env.now -
                                             self.prevous_time)*self.len
                    self.prevous_time = self.env.now
                    self.len -= 1
                self.server_busy = False
                self.start_idle_time = self.env.now


class Arrival_Process(object):
    def __init__(self, env, arrival_rate, server_process, max_len, Server_Idle_Periods, Packet_Delay):

        self.env = env
        self.arrival_rate = arrival_rate
        self.server_process = server_process
        self.Server_Idle_Periods = Server_Idle_Periods
        self.Packet_Delay = Packet_Delay
        self.packet_number = 0
        self.action = env.process(self.run())
        self.max_len = max_len
        self.packet_drop = 0

    def run(self):
        # packet arrivals
        # print("Arrival Process Started")

        while True:
            # Infinite loop for generating packets
            yield self.env.timeout(random.expovariate(self.arrival_rate))

            self.server_process.sum_time_length += (
                self.env.now - self.server_process.prevous_time)*self.server_process.len
            self.server_process.prevous_time = self.env.now

            # create and enque new packet
            self.packet_number += 1
            arrival_time = self.env.now
            new_packet = Packet(self.packet_number, arrival_time)
            # print(self.server_process.len)
            if len(self.server_process.queue) < self.max_len:
                self.server_process.len += 1
                self.server_process.queue.append(new_packet)
            else:
                self.packet_drop += 1

            if self.server_process.server_busy == False:
                self.server_process.server_busy = True
                idle_period = self.env.now - self.server_process.start_idle_time

                self.Server_Idle_Periods.addNumber(idle_period)
                self.server_process.action.interrupt()


class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


class StatObject(object):
    def __init__(self):
        self.dataset = []

    def addNumber(self, x):
        self.dataset.append(x)

    def sum(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum

    def mean(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum/n

    def maximum(self):
        return max(self.dataset)

    def minimum(self):
        return min(self.dataset)

    def count(self):
        return len(self.dataset)

    def median(self):
        self.dataset.sort()
        n = len(self.dataset)
        if n//2 != 0:  # get the middle number
            return self.dataset[n//2]
        else:  # find the average of the middle two numbers
            return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)

    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum/(len(self.dataset) - 1)
        return math.sqrt(sum)


def main():
    print("A finite buffer queuing system model: mu = {0}".format(G.MU))
    print("{0:<9} {1:<9} {2:<9} {3:<9} {4:<9} {5:<9}".format(
        "Lambda", "Max Len", "# Arrived", "# Dropped", "Drop Rate", "Theoretical"))
    random.seed(G.RANDOM_SEED)
    for arrival_rate in [0.1, 0.4, 0.8, 0.9]:
        for max_len in [1, 10, 50]:
            env = simpy.Environment()
            Server_Idle_Periods = StatObject()
            Packet_Delay = StatObject()
            server_process = Server_Process(
                env, Server_Idle_Periods, Packet_Delay)
            arrival_process = Arrival_Process(
                env, arrival_rate, server_process, max_len, Server_Idle_Periods, Packet_Delay)
            env.run(until=G.SIM_TIME)

            rho = arrival_rate / G.MU
            print("{0:<9.3f} {1:<9} {2:<9} {3:<9} {4:<9.5f} {5:<9.5f}".format(
                round(arrival_rate, 3),
                int(max_len),
                int(arrival_process.packet_number),
                int(arrival_process.packet_drop),
                round(arrival_process.packet_drop /
                      arrival_process.packet_number, 5),
                round((1-rho) * math.pow(rho, max_len+1) / (1 - math.pow(rho, max_len+2)), 5)))
        print()


if __name__ == '__main__':
    main()
