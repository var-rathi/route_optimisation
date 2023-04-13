# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from distance_matrix import distance_matrix
class plan_route(distance_matrix):
    def __init__(self,dates=['2023-02-01', '2023-02-02'],time_slots=['9:30 AM to 11:30 AM']):
        super().__init__(dates,time_slots)
        self.dist_matrix=self.euclidean_matrix_raw()
        self.speed=25 # km/hr
        self.time_per_delivery=10 #mins (for static time addition)
        self.time_equivalent=int((self.speed)*(self.time_per_delivery)*1000//3600)
    def create_data_model(self):
        data={}
        # data['distance_matrix'] = self.dist_matrix
        data['num_vehicles'] = 4
        data['depot']=0
        return data
    def create_routing_index_manager(self):
        self.manager = pywrapcp.RoutingIndexManager(len(self.dist_matrix),4, 0)
    def create_routing_model(self):
        self.routing = pywrapcp.RoutingModel(self.manager)
    # Create and register a transit callback.
    def distance_callback(self,from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = self.manager.IndexToNode(from_index)
        to_node = self.manager.IndexToNode(to_index)
        return self.dist_matrix[from_node][to_node]

    def print_solution(self):
        """Prints solution on console."""
        print(f'Objective: {self.solution.ObjectiveValue()}')
        max_route_distance = 0
        for vehicle_id in range(4):#4 here is the number of vehicles
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
        for vehicle_id in range(4):#4 here is the number of vehicles
            index = self.routing.Start(vehicle_id)
            vehicle_route[vehicle_id]={'route':[],'route_index':[],'route_distance':0}
            route_distance = 0
            while not self.routing.IsEnd(index):
                vehicle_route[vehicle_id]['route_index'].append(self.manager.IndexToNode(index))
                previous_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            vehicle_route[vehicle_id]['route_index'].append(self.manager.IndexToNode(index))
            vehicle_route[vehicle_id]['route_distance']=route_distance
        return vehicle_route

    def optimize_route(self):
        self.create_routing_index_manager()
        self.create_routing_model()
        self.transit_callback_index = self.routing.RegisterTransitCallback(self.distance_callback)
        # Define cost of each arc.
        self.routing.SetArcCostEvaluatorOfAllVehicles(self.transit_callback_index)
        # Add Distance constraint.
        dimension_name = 'Distance'
        self.routing.AddDimension(
            self.transit_callback_index,
            0,  # no slack
            300000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = self.routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)
        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        self.solution = self.routing.SolveWithParameters(search_parameters)
        # Print solution on console.
        if self.solution:
            return self.solution_listing()
        else:
            return {}

if __name__ == '__main__':
    # calc_distance=distance_matrix()
    # dis_mat=calc_distance.euclidean_matrix_raw()
    route_opt=plan_route()
    print(len(route_opt.data))
    print(route_opt.optimize_route())
    # print(dis_mat)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
