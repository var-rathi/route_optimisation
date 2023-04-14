# This is a sample Python script.
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time
from distance_matrix import distance_matrix
from route_optimisation import plan_route
if __name__ == '__main__':
    calc_distance=distance_matrix()
    print(list(calc_distance.data['weight']))
    k=list(calc_distance.list_dates()['dates'])
    l=[str(i) for i in k]
    print(l)
    # p=l,['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM']
    # dis_mat=calc_distance.euclidean_matrix_raw()
    #
    start_time = time.time()
    route_opt=plan_route(['2023-02-01', '2023-02-02', '2023-02-05'],['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM'])
    print("--- %s seconds ---" % (time.time() - start_time))
    start_time = time.time()
    print(len(route_opt.data))
    print(route_opt.visualise_route())
    print("--- %s seconds ---" % (time.time() - start_time))
    # print(route_opt.list_dates())
    print(route_opt.list_slots(['2023-02-06']))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
