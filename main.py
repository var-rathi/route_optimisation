# This is a sample Python script.
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time
from route_optimisation import plan_route

if __name__ == '__main__':

    start_time = time.time()
    route_opt=plan_route(['2023-02-01', '2023-02-02', '2023-02-05'],['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM'])
    print("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    print(len(route_opt.data))
    print(route_opt.visualise_route())


