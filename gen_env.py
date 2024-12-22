import torch

# Dữ liệu đầu vào
node_xy = torch.tensor([[[0.5, 0.5], [0.23, 0.32], [0.35, 0.53], [0.7, 0.4], [0.87, 0.9]]], dtype=torch.float)  # (batch, n, 2)
depot = torch.tensor([[0.0, 0.0]], dtype=torch.float)  # (batch, 2)
truck_num = torch.tensor([[[2, 2, 1, 0, 0]]], dtype=torch.int64)  # (batch, pomo, n)
cur_routes = torch.tensor([[[[0, 2, 0, 0, 0], [1, 3, 0, 0, 0], [4, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]],
                          dtype=torch.int64)  # (batch, pomo, n, n)



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


# routes_cost = get_routes_cost(cur_routes, node_xy, depot, truck_num)
# print(routes_cost)

