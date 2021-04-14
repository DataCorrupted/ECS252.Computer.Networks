import math
import csv


def get_mean(rho):
    return rho / (1 - rho)


def get_sd(rho):
    return math.sqrt(rho) / (1 - rho)


def export_to_csv():

    csv_name = '../plots/Q4.rho_mean_sd.csv'
    with open(csv_name, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=["rho", "mean", "sd"])

        csv_writer.writeheader()
        for rho in [x/10 for x in range(1, 10)]:
            csv_writer.writerow(
                {"rho": rho, "mean": get_mean(rho), "sd": get_sd(rho)})


export_to_csv()
