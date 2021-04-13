import math
import csv


def get_p_c(M, R, p, N):
    Nm = M // R
    if N <= Nm:
        return 0
    else:
        ret = 0
        for k in range(Nm+1):
            ret += math.comb(N, k) * math.pow(p, k) * math.pow(1-p, N-k)
        ret = 1 - ret
        return ret


def export_to_csv(M, R, p):

    csv_name = '../plots/Q3.Pc_N_{}_{}_{}.csv'.format(M, R, p)
    with open(csv_name, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=["N", "Pc"])

        csv_writer.writeheader()
        p_c = 0
        N = 0
        while p_c < 0.999:
            csv_writer.writerow({"N": N, "Pc": p_c})
            N += 1
            p_c = get_p_c(M, R, p, N)


def binary_search_M(N, R, p, p_c):
    l = 0
    r = N * R   # Max M needed
    m = (l + r) // 2
    while l + 1 < r:
        p_c_m = get_p_c(m, R, p, N)
        if p_c_m < p_c:
            r = m
        else:
            l = m
        m = (l + r) // 2
    return m


export_to_csv(1000, 200, 0.2)
export_to_csv(1000, 800, 0.01)

print("M should at least be {} Kbps".format(
    binary_search_M(20, 200, 0.2, 0.1)))
