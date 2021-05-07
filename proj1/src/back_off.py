import random


class BackOffImpl:
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
