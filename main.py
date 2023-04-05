# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
import os
from data_loader import data_loader_opsvone
if __name__ == '__main__':
    data_loader=data_loader_opsvone()

    print(data_loader.load_data(['2023-02-01', '2023-02-02'],['5:31 PM to 8:30 PM','5:31 PM to 8:30 PM']))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
