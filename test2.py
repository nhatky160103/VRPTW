import torch
from gen_env import get_routes_cost
from test import compute_total_distance

# Khởi tạo dữ liệu giả nhỏ
batch = 1
pomo = 1
n = 5

# Tạo dữ liệu giả
node_xy = torch.tensor([[[0.5, 0.5], [0.23, 0.32], [0.35, 0.53], [0.7, 0.4], [0.87, 0.9]]], dtype=torch.float)  # (batch, n, 2) -> tọa độ của khách hàng
depot = torch.tensor([[0.0, 0.0]], dtype=torch.float)  # (batch, 2) -> tọa độ depot
truck_num = torch.tensor([[[2, 2, 0, 0, 0]]], dtype=torch.int64)  # (batch, pomo, n) -> số lượng khách hàng trong mỗi lộ trình
cur_routes = torch.tensor([[[[0, 1, 0, 0, 0], [2, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]], dtype=torch.int64)  # (batch, pomo, n, n) -> lộ trình hiện tại
selected_node = torch.tensor([[4]], dtype=torch.int64)  # (batch, pomo) -> chỉ số khách hàng được chọn
service_time = torch.tensor([[0, 0, 0, 0, 0]] , dtype = torch.float32)
node_demand = torch.tensor([[1, 2, 1, 2, 1]] , dtype = torch.float32)
cur_demands = torch.tensor([[[ 3, 3, 0, 0, 0 ]]], dtype = torch.float32)
node_mask = torch.tensor([[[0, 0, 0, 0, 1]]], dtype = torch.float32)


routes_cost = get_routes_cost(cur_routes.clone(), node_xy.clone(), depot.clone(), truck_num.clone())

# print('routes_cost', routes_cost.shape)
# print('node_xy: ', node_xy.shape)
# print('depot: ',depot.shape)
# print('truck_num: ', truck_num.shape)
# print('cur_routes: ', cur_routes.shape)
# print('selected_node: ', selected_node.shape)
# print('service_time: ', service_time.shape)
# print('node_demand: ', node_demand.shape)
# print('cur_demands:', cur_demands.shape)
# print('node_mask:', node_mask.shape)


def update_route(node_xy, depot,node_demand,service_time, cur_demands, truck_num, cur_routes,routes_cost,  selected_node,node_mask, speed = 1.0):
    '''
    Update routes each decode time
    node_xy: Tensor shape (batch, n, 2) contains coord of n customer
    depot: Tensor shape (batch, 2)     contains coord of depot point
    truck_num: Tensor shape (batch, pomo, n) contains  number of customer in route, maximize n route, if just use m < n route, padding 0
    cur_routes: Tensor shape (batch, pomo, n, n) each routes contains index of customer, padding 0
    routes_cost: Tensor shape (batch, pomo, n, n + 1) cost of from right previous of each customer và cộng thêm servicetime, add value from last node to depot, padding 0
    selected_node: Tensor shape(batch, pomo) contains customer index chosen by model
    # selected_route: Tensor shape(batch, pomo) contain route index chosen by model
    Return:
        new_routes // same as cur_routes, but is inserted selected customer into selected route
        shape(batch, pomo, n, n)
        new_routes_cost shape(batch, pomo, n, n + 1)
        truck_num
        cur_demands
        insert_index
        selected_route_index
    '''
    batch, pomo, _, n = cur_routes.shape
    BATCH_IDX = torch.arange(batch)[:, None, None].expand(batch, pomo, n)
    POMO_IDX = torch.arange(pomo)[None, :, None].expand(batch, pomo, n)
    ROUTE_IDX =  torch.arange(pomo)[None, None, :].expand(batch, pomo, n)
    # raw_selected_route = selected_route.clone()
    # selected_route = selected_route.unsqueeze(-1)
    # node_num = torch.gather(truck_num, 2, selected_route) # shape (batch, pomo, 1)
    # node_num = node_num -1
    node_num = torch.where(truck_num - 1 < 0, 0, truck_num - 1)
    # selected_route_expand = selected_route.unsqueeze(-1).expand(-1, -1, 1, n)
    # nodes_route = torch.gather(cur_routes, 2, selected_route_expand).squeeze(2)
    nodes_route = cur_routes.clone() # shape (batch, pomo, n, n)
    node_xy_expand = node_xy.unsqueeze(1).expand(-1, pomo, -1, -1)
    raw_selected_node = selected_node.clone()
    selected_node = selected_node.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, 2)
    selected_node_coord = torch.gather(node_xy_expand, 2, selected_node).unsqueeze(2).expand(-1, -1, n, -1, -1) # shape( batch, pomo, 1, 2)
    nodes_route_expand = nodes_route.unsqueeze(-1).expand(-1,-1,-1, -1, 2) #shape (batch, pomo, n, n, 2 )
    nodes_route_coords = torch.gather(node_xy_expand.unsqueeze(2).expand(-1, -1,  n, -1, -1), 3, nodes_route_expand) #shape (batch, pomo, n, n, 2)
    node_num_expand = node_num.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, -1,1, 2) # shape(batch, pomo, 1, 2)
    last_node_coord = torch.gather(nodes_route_coords, 3, node_num_expand) #shape(batch, pomo,n,1, 2)
    depot_expand = depot.unsqueeze(1).unsqueeze(1).unsqueeze(1).expand(-1, pomo, n, 1, -1) #shape(batch, pomo,n,1, 2)
    distance_lastnode_depot = torch.sqrt(torch.sum((last_node_coord - depot_expand) ** 2, dim=-1))/speed
    #shape(batch, pomo,n, 1)
    distance_selected_depot = torch.sqrt(torch.sum((selected_node_coord - depot_expand) ** 2, dim=-1))/speed
    #shape(batch, pomo,n, 1)
    distances = torch.sqrt(torch.sum((selected_node_coord - nodes_route_coords) ** 2, dim=-1)) / speed
    # shape(batch, pomo,n,  n)
 
    range_tensor = torch.arange(n).unsqueeze(0).unsqueeze(0).unsqueeze(0) # Shape: (1, 1, 1, n)
   
    padding = range_tensor > node_num.unsqueeze(-1)
    padding = padding*10 #shape (batch, pomo, n, n)
    distances = distances + padding
 
    new_distances = distances.clone()
    new_distances = torch.concat((distance_selected_depot, new_distances), dim = 3) # shape (batch, pomo, n, n+1)
    node_num = node_num + 1
    distances[BATCH_IDX, POMO_IDX,ROUTE_IDX, node_num] = distance_lastnode_depot.squeeze(-1)
    distance_lastnode_depot = distance_lastnode_depot*10
    distances = torch.concat((distances,distance_lastnode_depot ), dim = 3) # shape (batch, pomo, n + 1)
    # lost_index = raw_selected_route.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, n + 1)
    # lost_distance = torch.gather(routes_cost, 2,lost_index ).squeeze(2) #shape(batch, pomo, n+1)
    inserted_cost = new_distances + distances - routes_cost #shape (batch, pomo,n, n + 1)
    node_mask = node_mask*20
    inserted_cost = inserted_cost + node_mask.unsqueeze(-1)
    min_indices = torch.argmin(inserted_cost.view(batch,pomo, -1), dim=2)
    selected_route_index = min_indices // inserted_cost.size(-1) # shape(batch, pomo)
    insert_index = min_indices % inserted_cost.size(-1) # shape (batch, pomo)
    # insert_index = torch.argmin(inserted_cost, dim = 3) # shape (batch, pomo, )
    selected_node_route = torch.gather(nodes_route, 2,selected_route_index.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, n)).squeeze(2)
    lost_distance = torch.gather(routes_cost, 2, selected_route_index.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, n + 1)).squeeze(2)
    selected_dis = torch.gather(distances, 2, selected_route_index.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, n + 1)).squeeze(2)
    selected_new_dis = torch.gather(new_distances, 2, selected_route_index.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, n + 1)).squeeze(2)
    new_nodes_route = torch.zeros((batch,pomo, n + 1), dtype= torch.int64)
    expanded_indices = torch.arange(n + 1).expand(batch,pomo, -1)  # Shape: (batch, n + 1)
    mask_before = expanded_indices < insert_index.unsqueeze(1)  # Shape: (batch, n+1)
    mask_after = expanded_indices > insert_index.unsqueeze(1)
    new_nodes_route[mask_before] = selected_node_route[mask_before[:, :, :-1]]
    new_nodes_route[mask_after] = selected_node_route[mask_after[:, :, 1:]]
    new_nodes_route[BATCH_IDX, POMO_IDX,  insert_index] = raw_selected_node
    cur_routes[BATCH_IDX, POMO_IDX, selected_route_index] = new_nodes_route[:, :, :-1]

    new_route_cost = torch.zeros((batch, pomo, n + 2))
    expanded_indices = torch.arange(n + 2).expand(batch,pomo, -1)  # Shape: (batch, n + 2)
    mask_before = expanded_indices < insert_index.unsqueeze(1)  # Shape: (batch, n+2)
    mask_after = expanded_indices > insert_index.unsqueeze(1)
    new_route_cost[mask_before] = lost_distance[mask_before[:, :, :-1]]
    lost_distance[BATCH_IDX, POMO_IDX, insert_index] = selected_dis[BATCH_IDX, POMO_IDX, insert_index]
    new_route_cost[mask_after] = lost_distance[mask_after[:, :, 1:]]
    new_route_cost[BATCH_IDX, POMO_IDX, insert_index] = selected_new_dis[BATCH_IDX, POMO_IDX, insert_index] +  service_time.unsqueeze(1).expand(-1, pomo, -1)[BATCH_IDX, POMO_IDX, raw_selected_node]
    routes_cost[BATCH_IDX, POMO_IDX, selected_route_index] = new_route_cost[:, :, :-1]
    truck_num[BATCH_IDX, POMO_IDX, selected_route_index]  += 1
 
 
    node_demand = node_demand.unsqueeze(1).expand(-1, pomo, -1)
    cur_demands[BATCH_IDX, POMO_IDX, selected_route_index] += node_demand[BATCH_IDX, POMO_IDX, raw_selected_node]
 
    return cur_routes, routes_cost, truck_num, cur_demands, insert_index,selected_route_index
 



cur_routes, routes_cost, truck_num, cur_demands, insert_index, selected_route_index = update_route(node_xy, depot, node_demand, service_time, cur_demands, truck_num, cur_routes, routes_cost,  selected_node, node_mask,)

print("New Routes:\n", cur_routes)                                                      

index_sequence = torch.tensor([[ 4, 2 ,  3]])

total_distance = compute_total_distance(node_xy, depot, index_sequence)
print('total_distance', total_distance)