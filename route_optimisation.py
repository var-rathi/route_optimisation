from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from distance_matrix import distance_matrix

import numpy as np
import matplotlib.pyplot as plt
class plan_route(distance_matrix):
    def __init__(self,dates=['2023-02-01', '2023-02-02'],time_slots=['9:30 AM to 11:30 AM']):
        super().__init__(dates,time_slots)
        # contains self.data --> Invoices, Weights, Location Coordinates
        self.dist_matrix=self.euclidean_matrix_raw()
    def create_distance_time_parameters(self):
        params={}
        params['speed']=25 #km/hr
        params['time_per_delivery']=10 # mins
        params['time_equivalent']=int(params['speed']*params['time_per_delivery']*1000//60)
        self.distance_time_parameters=params
    def create_vehicle_parameters(self):
        params={}
        params['vehicles_number']=20 #number of vehicles
        params['capacity']=[2500,2500,1200,1200,1200,1200,1200,2500,2500,1200,2500,2500,2500,2500,2500,2500,2500,1200,1200,1200] # Vehicle Capacity
        self.vehicle_parameters=params
    def create_routing_index_manager(self):
        # considering 0 as the depot we need to amend this
        self.manager = pywrapcp.RoutingIndexManager(len(self.dist_matrix),self.vehicle_parameters['vehicles_number'], 0)
    def create_routing_model(self):
        self.routing = pywrapcp.RoutingModel(self.manager)
    # Create and register a transit callback.
    def distance_callback(self,from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.dist_matrix[from_node][to_node]
    def time_callback(self,from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        # print(from_node,to_node)
        if to_node==0:
            # print(self.dist_matrix[from_node][to_node],self.dist_matrix[from_node][to_node])
            return self.dist_matrix[from_node][to_node]
        else:
            # print(self.dist_matrix[from_node][to_node],self.dist_matrix[from_node][to_node]+self.distance_time_parameters['time_equivalent'])
            return self.dist_matrix[from_node][to_node]+self.distance_time_parameters['time_equivalent']
    def weight_callback(self,from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        return list(self.data['weight'])[from_node]
    def print_solution(self):
        """Prints solution on console."""
        print(f'Objective: {self.solution.ObjectiveValue()}')
        max_route_distance = 0
        for vehicle_id in range(self.vehicle_parameters['vehicles_number']):#4 here is the number of vehicles
            index = self.routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            route_distance = 0
            while not self.routing.IsEnd(index):
                plan_output += ' {} -> '.format(self.manager.IndexToNode(index))
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            plan_output += '{}\n'.format(self.manager.IndexToNode(index))
            plan_output += 'Distance of the route: {}m\n'.format(route_distance)
            print(plan_output)
            max_route_distance = max(route_distance, max_route_distance)
        print('Maximum of the route distances: {}m'.format(max_route_distance))
    def solution_listing(self):
        vehicle_route={}
        for vehicle_id in range(self.vehicle_parameters['vehicles_number']):#4 here is the number of vehicles
            index = self.routing.Start(vehicle_id)
            vehicle_route[vehicle_id]={'route':[],'route_index':[],'route_distance':0,'route_time':0,'delivery_locations':0,'weight':0}
            route_distance = 0
            route_time =0
            weight=0
            while not self.routing.IsEnd(index):
                vehicle_route[vehicle_id]['route_index'].append(self.manager.IndexToNode(index))
                previous_index = index
                # print(index)
                index = self.solution.Value(self.routing.NextVar(index))
                route_time += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
                if self.manager.IndexToNode(index)!=0:
                    weight+=list(self.data['weight'])[self.manager.IndexToNode(index)]
                route_distance+=self.dist_matrix[self.manager.IndexToNode(previous_index)][self.manager.IndexToNode(index)]
            vehicle_route[vehicle_id]['route_index'].append(self.manager.IndexToNode(index))
            vehicle_route[vehicle_id]['route_time']=route_time
            vehicle_route[vehicle_id]['route_distance'] = route_distance
            vehicle_route[vehicle_id]['weight']=weight
            vehicle_route[vehicle_id]['delivery_locations']=max(0,len(vehicle_route[vehicle_id]['route_index'])-2)
        return vehicle_route
    def optimize_route(self):
        self.data.weight[0]=0 # Depot weight is being initialized to zero
        self.create_distance_time_parameters()
        self.create_vehicle_parameters()
        self.create_routing_index_manager()
        self.create_routing_model()
        self.transit_callback_index = self.routing.RegisterTransitCallback(self.time_callback)

        # Define cost of each arc.
        self.routing.SetArcCostEvaluatorOfAllVehicles(self.transit_callback_index)
        self.transit_callback_index_2 = self.routing.RegisterTransitCallback(self.time_callback)
        #Weight capacity constraint
        self.weight_callback_index = self.routing.RegisterUnaryTransitCallback(self.weight_callback)
        self.weight_callback_index_2 = self.routing.RegisterUnaryTransitCallback(self.weight_callback)
        self.weight_callback_index_3 = self.routing.RegisterUnaryTransitCallback(self.weight_callback)
        # Add Distance constraint.
        dimension_name = 'Time'
        self.routing.AddDimension(
            self.transit_callback_index,
            0,  # no slack
            int(self.distance_time_parameters['speed']*5*1000),  # vehicle maximum travel time 2.5 hours
            True,  # start cumul to zero
            dimension_name)
        self.routing.AddDimension(
            self.transit_callback_index_2,
            0,  # no slack
            int(self.distance_time_parameters['speed']*5*1000),  # vehicle maximum travel time 2.5 hours
            True,  # start cumul to zero
            'time_callback_index_2')
        self.routing.AddDimensionWithVehicleCapacity(
            self.weight_callback_index,
            0,  # null capacity slack
            np.array(self.vehicle_parameters['capacity'])*4,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Weight')
        self.routing.AddDimensionWithVehicleCapacity(
            self.weight_callback_index_2,
            0,  # null capacity slack
            np.array(self.vehicle_parameters['capacity'])*4,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Weight_2')
        self.routing.AddDimensionWithVehicleCapacity(
            self.weight_callback_index_3,
            0,  # null capacity slack
            np.array(self.vehicle_parameters['capacity'])*4,  # vehicle maximum capacities
            True,  # start cumul to zero
            'Weight_3')
        # Minimizing net time travelled by all the vehicles also keeping time in limits
        time_dimension = self.routing.GetDimensionOrDie(dimension_name)
        time_dimension_2 = self.routing.GetDimensionOrDie('time_callback_index_2')
        weight_dimension=self.routing.GetDimensionOrDie('Weight')
        weight_dimension_2 = self.routing.GetDimensionOrDie('Weight_2')
        weight_dimension_3 = self.routing.GetDimensionOrDie('Weight_3')
        # time_dimension.SetGlobalSpanCostCoefficient(1)
        for vehicle_id in range(self.vehicle_parameters['vehicles_number']):
            index = self.routing.End(vehicle_id)
            time_dimension_2.SetCumulVarSoftUpperBound(index,int(self.distance_time_parameters['speed']*2*1000), 4000)
            time_dimension.SetCumulVarSoftUpperBound(index, int(self.distance_time_parameters['speed'] * 3.5 * 1000), 100000)
            weight_dimension.SetCumulVarSoftUpperBound(index,int(self.vehicle_parameters['capacity'][vehicle_id] ), 500)
            weight_dimension_2.SetCumulVarSoftUpperBound(index, int(self.vehicle_parameters['capacity'][vehicle_id]*1.3), 5000)
            weight_dimension_3.SetCumulVarSoftUpperBound(index,int(self.vehicle_parameters['capacity'][vehicle_id] * 2), 500000)
        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        # search_parameters.solution_limit = 1
        search_parameters.time_limit.seconds = 180

        search_parameters.log_search = 1
        self.solution = self.routing.SolveWithParameters(search_parameters)
        # Print solution on console.
        if self.solution:
            print(self.solution.ObjectiveValue())
            sol=self.solution_listing()
            return sol
        else:
            return {}
    def connectpoints(self,x1,y1,x2, y2,color):
        plt.plot([x1, x2], [y1, y2], c=color)
    def visualise_route(self):
        sol=self.optimize_route()
        color = ['blue', 'black', 'red', 'green', 'orange', 'brown']
        c = 0
        xy = self.convert_to_xy()
        xy = xy - xy[0] # depot is subtracted for balancing things
        # print(xy)
        print(sol)
        if sol:
            for vehicle_id in sol.keys():
                if len(sol[vehicle_id]['route_index'])==2:
                    continue
                for i in range(len(sol[vehicle_id]['route_index']) - 1):

                    a, b = xy[sol[vehicle_id]['route_index'][i]], xy[sol[vehicle_id]['route_index'][i+1]]
                    # print(vehicle_id,a,b)
                    self.connectpoints(a[0], a[1], b[0], b[1], color[c % len(color)])
                c += 1
            plt.scatter(xy[:, 0], xy[:, 1], c="blue", s=10)
            plt.show()

        net_route_time = 0
        cost_2hrs = 0
        cost_3hrs = 0
        costnormalweight = 0
        cost30weight = 0
        cost2weight = 0
        for vehicle_id in range(self.vehicle_parameters['vehicles_number']):
            net_route_time += sol[vehicle_id]['route_time']

            cost_2hrs += 4000 * max(0, sol[vehicle_id]['route_time'] - int(self.distance_time_parameters['speed'] * 2 * 1000))
            # print(max(0,sol[vehicle_id]['route_time']-int(self.distance_time_parameters['speed']*2*1000)))
            cost_3hrs += 100000 * max(0, sol[vehicle_id]['route_time'] - int(
                self.distance_time_parameters['speed'] * 3.5 * 1000))
            costnormalweight += 500 * max(0, sol[vehicle_id]['weight'] - int(
                self.vehicle_parameters['capacity'][vehicle_id]))
            cost30weight += 5000 * max(0, sol[vehicle_id]['weight'] - int(self.vehicle_parameters['capacity'][vehicle_id] * 1.3))
            cost2weight += 500000 * max(0, sol[vehicle_id]['weight'] - int(self.vehicle_parameters['capacity'][vehicle_id] * 2))
        print('net_route_time: {}'.format(net_route_time))
        print('cost_2hrs: {}'.format(cost_2hrs))
        print('cost_3hrs: {}'.format(cost_3hrs))
        print('costnormalweight: {}'.format(costnormalweight))
        print('cost30weight: {}'.format(cost30weight))
        print('cost2weight: {}'.format(cost2weight))
        print('Net_Cost: {}'.format(net_route_time + cost_3hrs + cost_2hrs + costnormalweight + cost2weight + cost30weight))
