# This is a sample Python script.
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time

# from route_optimisation import plan_route
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from distance_matrix import distance_matrix

import numpy as np
import matplotlib.pyplot as plt
def create_distance_time_parameters():
    params = {}
    params['speed'] = 25  # km/hr
    params['time_per_delivery'] = 10  # mins
    params['time_equivalent'] = int(params['speed'] * params['time_per_delivery'] * 1000 // 60)
    return params
def create_vehicle_parameters(self):
    params={}
    params['vehicles_number']=15 #number of vehicles
    params['capacity']=[2500,2500,1200,1200,1200,1200,1200,2500,2500,1200,2500,2500,2500,2500,2500] # Vehicle Capacity
    return params
def solution_listing(vehicle_parameters,routing,manager,solution,data,dist_matrix):
    vehicle_route={}
    for vehicle_id in range(vehicle_parameters['vehicles_number']):#4 here is the number of vehicles
        index = routing.Start(vehicle_id)
        vehicle_route[vehicle_id]={'route':[],'route_index':[],'route_distance':0,'route_time':0,'delivery_locations':0,'weight':0}
        route_distance = 0
        route_time =0
        weight=0
        while not routing.IsEnd(index):
            vehicle_route[vehicle_id]['route_index'].append(manager.IndexToNode(index))
            previous_index = index
            # print(index)
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
            if manager.IndexToNode(index)!=0:
                weight+=list(data['weight'])[manager.IndexToNode(index)]
            route_distance+=dist_matrix[manager.IndexToNode(previous_index)][manager.IndexToNode(index)]
        vehicle_route[vehicle_id]['route_index'].append(manager.IndexToNode(index))
        vehicle_route[vehicle_id]['route_time']=route_time
        vehicle_route[vehicle_id]['route_distance'] = route_distance
        vehicle_route[vehicle_id]['weight']=weight
        vehicle_route[vehicle_id]['delivery_locations']=max(0,len(vehicle_route[vehicle_id]['route_index'])-2)
    return vehicle_route
def optimize_route(self,dates=['2023-02-01', '2023-02-02'],time_slots=['9:30 AM to 11:30 AM']):
    d_m  = distance_matrix(dates,time_slots)
    dist_matrix = d_m.euclidean_matrix_raw()
    data = d_m.data

    distance_time_parameters=create_distance_time_parameters()

    vehicle_parameters=create_vehicle_parameters()
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix),vehicle_parameters['vehicles_number'], 0)
    routing = pywrapcp.RoutingModel(manager)
    ##################################################
    def time_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # print(from_node,to_node)
        if to_node==0:
            # print(self.dist_matrix[from_node][to_node],self.dist_matrix[from_node][to_node])
            return dist_matrix[from_node][to_node]
        else:
            # print(self.dist_matrix[from_node][to_node],self.dist_matrix[from_node][to_node]+self.distance_time_parameters['time_equivalent'])
            return dist_matrix[from_node][to_node]+distance_time_parameters['time_equivalent']
    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    #######################################################
    def weight_callback(self,from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return list(data['weight'])[from_node]
    #Weight capacity constraint
    weight_callback_index = routing.RegisterUnaryTransitCallback(weight_callback)
    # Add Distance constraint.
    dimension_name = 'Time'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        int(self.distance_time_parameters['speed']*5*1000),  # vehicle maximum travel time 2.5 hours
        True,  # start cumul to zero
        dimension_name)
    routing.AddDimensionWithVehicleCapacity(
        weight_callback_index,
        0,  # null capacity slack
        np.array(self.vehicle_parameters['capacity'])*4,  # vehicle maximum capacities
        True,  # start cumul to zero
        'Weight')
    # Minimizing net time travelled by all the vehicles also keeping time in limits
    time_dimension = routing.GetDimensionOrDie(dimension_name)
    weight_dimension = routing.GetDimensionOrDie('Weight')
    time_dimension.SetGlobalSpanCostCoefficient(1)
    for vehicle_id in range(vehicle_parameters['vehicles_number']):
        index = routing.End(vehicle_id)
        time_dimension.SetCumulVarSoftUpperBound(index,int(distance_time_parameters['speed']*2*1000), 1000)
        time_dimension.SetCumulVarSoftUpperBound(index, int(distance_time_parameters['speed'] * 3.5 * 1000), 100000)
        weight_dimension.SetCumulVarSoftUpperBound(index,int(vehicle_parameters['capacity'][vehicle_id] ), 500)
        weight_dimension.SetCumulVarSoftUpperBound(index, int(vehicle_parameters['capacity'][vehicle_id]*1.3), 5000)
        weight_dimension.SetCumulVarSoftUpperBound(index,int(vehicle_parameters['capacity'][vehicle_id] * 2), 500000)
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.solution_limit = 1
    # search_parameters.time_limit.seconds = 90

    search_parameters.log_search = 1
    solution = routing.SolveWithParameters(search_parameters)
    # Print solution on console.
    net_route_time = 0
    cost_2hrs = 0
    cost_3hrs = 0
    costnormalweight = 0
    cost30weight = 0
    cost2weight = 0
    # for vehicle_id in range(vehicle_parameters['vehicles_number']):
    #     net_route_time += sol[vehicle_id]['route_time']
    #
    #     cost_2hrs += 4000 * max(0, sol[vehicle_id]['route_time'] - int(distance_time_parameters['speed'] * 2 * 1000))
    #     # print(max(0,sol[vehicle_id]['route_time']-int(self.distance_time_parameters['speed']*2*1000)))
    #     cost_3hrs += 100000 * max(0, sol[vehicle_id]['route_time'] - int(distance_time_parameters['speed'] * 3.5 * 1000))
    #     costnormalweight += 500 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id]))
    #     cost30weight += 5000 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id] * 1.3))
    #     cost2weight += 500000 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id] * 2))
    # print('net_route_time: {}'.format(net_route_time))
    # print('cost_2hrs: {}'.format(cost_2hrs))
    # print('cost_3hrs: {}'.format(cost_3hrs))
    # print('costnormalweight: {}'.format(costnormalweight))
    # print('cost30weight: {}'.format(cost30weight))
    # print('cost2weight: {}'.format(cost2weight))
    # print('Net_Cost: {}'.format(net_route_time + cost_3hrs + cost_2hrs + costnormalweight + cost2weight + cost30weight))

    if solution:
        print('Actual Cost Function: ',solution.ObjectiveValue())
        sol=solution_listing(vehicle_parameters,routing,manager,solution,data,dist_matrix)
        for vehicle_id in range(vehicle_parameters['vehicles_number']):
            net_route_time += sol[vehicle_id]['route_time']

            cost_2hrs += 4000 * max(0,sol[vehicle_id]['route_time'] - int(distance_time_parameters['speed'] * 2 * 1000))
            # print(max(0,sol[vehicle_id]['route_time']-int(self.distance_time_parameters['speed']*2*1000)))
            cost_3hrs += 100000 * max(0, sol[vehicle_id]['route_time'] - int(distance_time_parameters['speed'] * 3.5 * 1000))
            costnormalweight += 500 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id]))
            cost30weight += 5000 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id] * 1.3))
            cost2weight += 500000 * max(0, sol[vehicle_id]['weight'] - int(vehicle_parameters['capacity'][vehicle_id] * 2))
        print('net_route_time: {}'.format(net_route_time))
        print('cost_2hrs: {}'.format(cost_2hrs))
        print('cost_3hrs: {}'.format(cost_3hrs))
        print('costnormalweight: {}'.format(costnormalweight))
        print('cost30weight: {}'.format(cost30weight))
        print('cost2weight: {}'.format(cost2weight))
        print('Net_Cost: {}'.format(
            net_route_time + cost_3hrs + cost_2hrs + costnormalweight + cost2weight + cost30weight))

        return sol
    else:
        return {}

if __name__ == '__main__':
    calc_distance=distance_matrix()
    print(list(calc_distance.data['weight']))
    k=list(calc_distance.list_dates()['dates'])
    l=[str(i) for i in k]
    print(l)
    # # p=l,['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM']
    # # dis_mat=calc_distance.euclidean_matrix_raw()
    # #
    # start_time = time.time()
    # route_opt=plan_route(['2023-02-01', '2023-02-02', '2023-02-05'],['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM'])
    # print("--- %s seconds ---" % (time.time() - start_time))
    # start_time = time.time()
    print(optimize_route(['2023-02-01', '2023-02-02', '2023-02-05'],['2:31 PM to 5:30 PM','11:31 AM to 1:30 PM','9:30 AM to 11:30 AM','5:31 PM to 8:30 PM']))
    # print(len(route_opt.data))
    # print(route_opt.visualise_route())
    # # route_opt.print_costs()
    # print("--- %s seconds ---" % (time.time() - start_time))
    # # print(route_opt.list_dates())
    # # print(route_opt.list_slots(['2023-02-06']))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
