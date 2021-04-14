import math
import csv


def get_rk_div_kfac(m, rho, mem={0: 1}):
    if m not in mem:
        mem[m] = get_rk_div_kfac(m-1, rho, mem) * rho / m
    return mem[m]


def export_to_csv(M=24, mu=1/180):

    csv_name = '../plots/Q6.P_blocking_M_{}.csv'.format(M)
    with open(csv_name, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(
            csv_file, fieldnames=["lambda", "rho", "P"])

        csv_writer.writeheader()
        for rho in [0.1, 0.2, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8]:
            mem = {0: 1}
            divisor = get_rk_div_kfac(M, rho, mem)
            dividend = 0
            for m in range(M+1):
                dividend += get_rk_div_kfac(m, rho, mem)
            p = divisor / dividend
            csv_writer.writerow({"lambda": rho*mu, "rho": rho, "P": p})


export_to_csv()
