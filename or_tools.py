"""Vehicles Routing Problem (VRP) with Time Windows."""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from read_data import get_data
import math

def create_data_model(test_case):
    """Stores the data for the problem."""

    m, Q, D, e0, l0, cost_matrix, customers = get_data(test_case)
    data = {}

    data["time_matrix"] = cost_matrix

    time_window = [customer.time_window for customer in customers]
    total_load = 0
    for customer in customers:
        total_load += customer.demand

    data["time_windows"] = time_window
    data["num_vehicles"] = math.ceil(total_load/Q)  # định nghĩa số lượng xe khi không có đầu vào
    data["depot"] = 0
    return data


# def print_solution(data, manager, routing, solution):
#     """Prints solution on console."""
#     print(f"Objective: {solution.ObjectiveValue()}")
#     time_dimension = routing.GetDimensionOrDie("Time")
#     total_time = 0
#     for vehicle_id in range(data["num_vehicles"]):
#         index = routing.Start(vehicle_id)
#         plan_output = f"Route for vehicle {vehicle_id}:\n"
#         while not routing.IsEnd(index):
#             time_var = time_dimension.CumulVar(index)
#             plan_output += (
#                 f"{manager.IndexToNode(index)}"
#                 f" Time({solution.Min(time_var)},{solution.Max(time_var)})"
#                 " -> "
#             )
#             index = solution.Value(routing.NextVar(index))
#         time_var = time_dimension.CumulVar(index)
#         plan_output += (
#             f"{manager.IndexToNode(index)}"
#             f" Time({solution.Min(time_var)},{solution.Max(time_var)})\n"
#         )
#         plan_output += f"Time of the route: {solution.Min(time_var)}min\n"
#         print(plan_output)
#         total_time += solution.Min(time_var)
#     print(f"Total time of all routes: {total_time}min")

def print_solution(data, manager, routing, solution):
    """Prints solution as a list of routes."""
    routes = []
    for vehicle_id in range(data["num_vehicles"]):
        route = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        # route.append(manager.IndexToNode(index))  # Append the depot at the end
        if len(route)!= 1:
            routes.append(route)
    print(routes)
    return routes


def get_routes(test_case):
    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data_model(test_case)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["time_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["time_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = "Time"
    routing.AddDimension(
        transit_callback_index,
        30,  # allow waiting time
        30,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time,
    )
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data["time_windows"]):
        if location_idx == data["depot"]:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    depot_idx = data["depot"]
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(
            data["time_windows"][depot_idx][0], data["time_windows"][depot_idx][1]
        )

    # Instantiate route start and end times to produce feasible times.
    for i in range(data["num_vehicles"]):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i))
        )
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(i)))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        routes = print_solution(data, manager, routing, solution)
        return routes

if __name__ == "__main__":
    test_case= input('input the test case:... ')
    routes = get_routes(test_case)