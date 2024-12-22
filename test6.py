import torch


import torch

batch = 1
m = 1
n = 5

node_xy = torch.tensor([[[0.5, 0.5], [0.23, 0.32], [0.35, 0.53], [0.7, 0.4], [0.87, 0.9]]], dtype=torch.float32)  # (batch, n, 2) -> tọa độ của khách hàng
depot = torch.tensor([[0.0, 0.0]], dtype=torch.float32)  # (batch, 2) -> tọa độ depot
node_demand = torch.tensor([[1, 2, 3, 2, 4]], dtype = torch.float32) # (batch, n) -> nhu cầu của của từng node
service_time = torch.tensor([[0, 0, 0, 0, 0]], dtype = torch.float32)
truck_num = torch.tensor([[[1, 1, 0, 0, 0]]], dtype=torch.int64)  # (batch, pomo, n) -> số lượng khách hàng trong mỗi lộ trình
node_indices = torch.tensor([[0, 2, 0, 0, 0]], dtype= torch.int64) # (batch, n) -> đỉnh bắt đầu của mỗi route
max_duration = torch.tensor([2.4], dtype= torch.float32) # (batch)




def init_travel_time_demand( depot, node_xy, node_demand, service_time,  node_indices, max_duration, truck_num, speed=1.0):
    """
    Computes the travel time from the depot to a set of nodes identified by indices.

    Args:
        depot_xy (torch.Tensor): Tensor of shape (batch, 1, 2) representing depot coordinates.
        node_xy (torch.Tensor): Tensor of shape (batch, n, 2) representing coordinates of all nodes.
        node_demand: Tensor of shape(batch, n)
        node_indices (torch.Tensor): Tensor of shape (batch, m) containing indices of nodes to calculate travel time for.
        truck_num: Tensor shape (batch, n)
        speed (float): Travel speed, default is 1.0.

    Returns:
        torch.Tensor: Tensor of shape (batch, m) representing travel times from depot to each selected node.
    """
    # Gather node coordinates using the indices
    routes_demand = torch.gather(node_demand, 1, node_indices)
    routes_demand = routes_demand * truck_num

    selected_node_xy = torch.gather(node_xy, 1, node_indices.unsqueeze(-1).expand(-1, -1, 2))  # Shape: (batch, m, 2)
    selected_service_time= torch.gather(service_time, 1, node_indices )
    # Compute the difference in coordinates
    delta = selected_node_xy - depot  # Shape: (batch, m, 2)

    # Compute Euclidean distances
    distances = torch.sqrt(torch.sum(delta ** 2, dim=-1))  # Shape: (batch, m)

    # Compute travel time by dividing distance by speed
    travel_times = distances / speed 
    batch, m = travel_times.shape

    # Apply mask to travel_time
    travel_times = travel_times * truck_num  # Masked values are set to 0
    
    n = node_xy.size(1)

    # Initialize result matrix with zeros
    travel_matrix = torch.zeros((batch, n, n + 1), device=travel_times.device)

    # Fill the first m values of each row in the n x n matrix
    travel_matrix[:, :m, 0] = travel_times + selected_service_time
    travel_matrix[:, :m, 1] = travel_times


    distances= torch.sqrt(torch.sum((selected_node_xy.unsqueeze(1) - node_xy.unsqueeze(2)) ** 2, dim=-1)).unsqueeze(-1)/speed  # shape (batch, n, n, 1)
    xy_depot = torch.sqrt(torch.sum((depot.unsqueeze(1).unsqueeze(1) - node_xy.unsqueeze(2)) ** 2, dim = -1)).unsqueeze(2).expand(-1, -1, n, 1)/ speed #shape(batch, n,n, 1)

    distances = distances + xy_depot  + service_time.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, n, 1) + selected_service_time.unsqueeze(1).unsqueeze(-1).expand(-1, n, n, 1)

    cost =  distances > max_duration.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)



    routes_matrix = torch.zeros((batch, n, n ), device=travel_times.device)
    routes_matrix[:, :m, 0] = node_indices

   
    return travel_matrix, routes_matrix, routes_demand, cost.squeeze(-1)


travel_matrix, routes_matrix, routes_demand, cost = init_travel_time_demand(depot, node_xy, node_demand, service_time,  node_indices, max_duration, truck_num)
                                                                                


print('travel_matrix: ', travel_matrix)


print("routes_matrix:",routes_matrix )


print('routes_demand', routes_demand)


print('cost', cost)