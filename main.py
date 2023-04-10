# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
import os
from distance_matrix import distance_matrix
if __name__ == '__main__':
    calc_distance=distance_matrix()
    dis_mat=calc_distance.euclidean_matrix_raw()
    print(dis_mat)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
