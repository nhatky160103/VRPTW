import torch
from test import compute_total_distance

def get_routes_cost(cur_routes, node_xy, depot, truck_num):
    batch, pomo, n, _ = cur_routes.shape

    # Kết hợp depot và node_xy để tạo danh sách tọa độ đầy đủ
    full_node_xy = torch.cat([depot.unsqueeze(1), node_xy], dim=1)  # (batch, n+1, 2)

    routes_cost = torch.zeros((batch, pomo, n, n + 1), dtype=torch.float)  # Kích thước (batch, pomo, n, n+1)

    for b in range(batch):
        for p in range(pomo):
            for t in range(n):
                num_customer = truck_num[b, p, t]
                if num_customer > 0:

                    route = cur_routes[b, p, t]
                    route[: num_customer] += 1
                    valid_nodes = route[route > 0]
                    if len(valid_nodes) == 0:
                        continue

                    full_route = torch.cat([torch.tensor([0]), valid_nodes, torch.tensor([0])])
                    route_coords = full_node_xy[b, full_route]

                    distances = torch.sqrt(((route_coords[:-1] - route_coords[1:]) ** 2).sum(dim=-1))
                    routes_cost[b, p, t, :len(distances)] = distances

    return routes_cost



# test case chèn vào đầu và ở cuối và ở giữa
# một đỉnh 5 bị mask, mà chuển thành không bị mask
# Check các trường hợp sau
# trc khi update route thì đỉnh đó  không bị mask, sau đó bị mask
# trc khi update bị mask, sau bị mask
# trước không sau không
# trước có sau có

batch = 1
m = 1
n = 5

node_xy = torch.tensor([[[0.5, 0.5], [0.23, 0.32], [0.35, 0.53], [0.7, 0.4], [0.87, 0.9]]], dtype=torch.float32)  # (batch, n, 2) -> tọa độ của khách hàng
depot = torch.tensor([[0.0, 0.0]], dtype=torch.float32)  # (batch, 2) -> tọa độ depot
node_demand = torch.tensor([[1, 2, 3, 2, 4]], dtype = torch.float32) # (batch, n) -> nhu cầu của của từng node
service_time = torch.tensor([[0, 0, 0, 0, 0]], dtype = torch.float32)
max_duration = torch.tensor([2.4], dtype= torch.float32) # (batch)
truck_num = torch.tensor([[[3, 1, 0, 0, 0]]], dtype=torch.int64)  # (batch, pomo, n) -> số lượng khách hàng trong mỗi lộ trình
node_indices = torch.tensor([[0, 2, 0, 0, 0]], dtype= torch.int64) # (batch, n) -> đỉnh bắt đầu của mỗi route
selected_route = torch.tensor([[0]], dtype=torch.int64)  # (batch, pomo) -> chỉ số lộ trình được chọn
old_routes = torch.tensor([[[[0, 3, 0, 0, 0], [2, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]], dtype=torch.int64) 
cur_routes = torch.tensor([[[[0, 4, 3, 0, 0], [2, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]], dtype=torch.int64)  # (batch, pomo, n, n) -> lộ trình hiện tại
cur_mask = torch.tensor([[[[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [0, 0, 0, 0, 0]]]], dtype=torch.int64)  # (batch, pomo, n, n)

expech_mask = cur_mask = torch.tensor([[[[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0]]]], dtype=torch.int64)  

routes_cost = get_routes_cost(cur_routes.clone(), node_xy.clone(), depot.clone(), truck_num.clone())

index_sequence = torch.tensor([[  0, 1, 3]], dtype  = torch.int64)
distance = compute_total_distance(node_xy, depot, index_sequence)
print(distance)

# print(routes_cost)

def update_duration_mask(cur_mask, cur_routes, routes_cost, service_time,   max_duration, truck_num, selected_route, node_xy, depot, speed = 1.0):
    batch, pomo, n, _ = cur_routes.shape
   
    BATCH_IDX = torch.arange(batch)[:, None, None].expand(batch, pomo, n)
    POMO_IDX = torch.arange(pomo)[None, :, None].expand(batch, pomo, n)
    ROUTE_IDX =  torch.arange(pomo)[None, None, :].expand(batch, pomo, n)
    


    selected_route_cost = torch.gather(routes_cost, 2, selected_route.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, -1, n+ 1)).squeeze(2)
    nodes_route = torch.gather(cur_routes, 2, selected_route.unsqueeze(-1).unsqueeze(-1)).expand(-1, -1, -1 , n).squeeze(2)
    selected_route_service_time = torch.gather(service_time.unsqueeze(1).expand(-1, pomo, -1), 2, nodes_route) # shape (batch, pomo, n)


    nodes_num = torch.gather(truck_num, 2, selected_route.unsqueeze(-1)).expand(batch, pomo, n)
    total_cost = torch.sum(selected_route_cost, dim = 2)
    # suspect_pos = torch.concat((nodes_route[BATCH_IDX, POMO_IDX,cur_index].unsqueeze(-1), nodes_route[BATCH_IDX, POMO_IDX,cur_index -1].unsqueeze(-1), nodes_route[BATCH_IDX, POMO_IDX,cur_index -1].unsqueeze(-1)), 2)
    node_xy_expand = node_xy.unsqueeze(1).expand(-1, pomo, -1, -1)
    nodes_route_coords = torch.gather(node_xy_expand, 2, nodes_route.unsqueeze(-1).expand(-1, -1, -1, 2)) #shape (batch, pomo, 3, 2)
    nodes_num = nodes_num - 1
    # nodes_route_coords[:, :, 2, :] = torch.where(cur_index.unsqueeze(-1).expand(-1, -1, 2) < nodes_num.unsqueeze(-1).expand(-1, -1, 2), nodes_route_coords[:, :, 2, :], depot.unsqueeze(1).expand(-1, pomo, -1))
    distances= torch.sqrt(torch.sum((nodes_route_coords.unsqueeze(2) - node_xy_expand.unsqueeze(3)) ** 2, dim=-1))/speed  # shape (batch, pomo, n, n)
    xy_depot = torch.sqrt(torch.sum((depot.unsqueeze(1).unsqueeze(2).unsqueeze(2).expand(-1, pomo, 1,1, -1) - node_xy_expand.unsqueeze(3)) ** 2, dim = -1))/ speed #shape(batch, pomo, n, 1)
 
    range_tensor = torch.arange(n).unsqueeze(0).unsqueeze(0).unsqueeze(0)# Shape: (1, 1, 1, n)
 
    padding = range_tensor > nodes_num.unsqueeze(-1)
    padding = padding*10 #shape (batch, pomo, n, n)
    distances = distances + padding
    new_distances = distances.clone()
    new_distances = torch.concat((xy_depot, new_distances), dim = 3) # shape (batch, pomo, n, n+1)
    distances[BATCH_IDX, POMO_IDX,ROUTE_IDX, nodes_num+ 1] = xy_depot.squeeze(-1)
    selected_route_service_time = selected_route_service_time.unsqueeze(2).expand(-1, -1, n, -1)
    zero = torch.zeros((batch, pomo, n))
    
    # print(nodes_num.shape)
    # print(selected_route_service_time.shape)
    # print(service_time.shape)
    # print(zero.shape)

    selected_route_service_time[BATCH_IDX, POMO_IDX, ROUTE_IDX, nodes_num+ 1] = zero
    xy_depot = xy_depot*500
 
    selected_route_service_time = torch.concat((selected_route_service_time,xy_depot ), dim = 3) # shape (batch, pomo, n, n + 1)
 
    distances = torch.concat((distances,xy_depot ), dim = 3) # shape (batch, pomo, n + 1)

    cost = new_distances + distances - selected_route_cost.unsqueeze(2) + selected_route_service_time + service_time.unsqueeze(1).unsqueeze(-1).expand(batch, pomo, n , 1) + \
    total_cost.unsqueeze(-1).unsqueeze(-1)<= max_duration.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
    

    mask = torch.sum(cost.to(torch.int64), dim = -1) == 0 # shape(batch, pomo, n)
    mask = mask.to(torch.int64)
 
    
    cur_mask[BATCH_IDX.squeeze(-1), POMO_IDX.squeeze(-1), :,  selected_route] = mask
 
    return cur_mask
 

cur_mask=  update_duration_mask(cur_mask, cur_routes, routes_cost, service_time,   max_duration, truck_num, selected_route, node_xy, depot)
print(cur_mask)