import torch

# # Khởi tạo dữ liệu giả nhỏ
# batch = 1
# pomo = 1
# n = 5

# # Tạo dữ liệu giả
# node_xy = torch.tensor([[[0.5, 0.5], [0.23, 0.32], [0.35, 0.53], [0.7, 0.4], [0.87, 0.9]]], dtype=torch.float)  # (batch, n, 2) -> tọa độ của khách hàng
# depot = torch.tensor([[0.0, 0.0]], dtype=torch.float)  # (batch, 2) -> tọa độ depot
# truck_num = torch.tensor([[[2, 2, 0, 0, 0]]], dtype=torch.int64)  # (batch, pomo, n) -> số lượng khách hàng trong mỗi lộ trình
# cur_routes = torch.tensor([[[[0, 1, 0, 0, 0], [2, 3, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]]], dtype=torch.int64)  # (batch, pomo, n, n) -> lộ trình hiện tại
# selected_node = torch.tensor([[4]], dtype=torch.int64)  # (batch, pomo) -> chỉ số khách hàng được chọn
# selected_route = torch.tensor([[0]], dtype=torch.int64)  # (batch, pomo) -> chỉ số lộ trình được chọn


# print('node_xy: ', node_xy.shape)
# print('depot: ',depot.shape)
# print('truck_num: ', truck_num.shape)
# print('cur_routes: ', cur_routes.shape)
# print('selected_node: ', selected_node.shape)
# print('selected_route: ', selected_route.shape)


# def update_route(node_xy, depot, truck_num, cur_routes, selected_node, selected_route, speed=1.0):
#     '''
#     Update routes each decode time
#     node_xy: Tensor shape (batch, n, 2) contains coord of n customer
#     depot: Tensor shape (batch, 2)     contains coord of depot point
#     truck_num: Tensor shape (batch, pomo, n) contains  number of customer in route, maximize n route, if just use m < n route, padding 0
#     cur_routes: Tensor shape (batch, pomo, n, n) each routes contains index of customer, padding 0
#     selected_node: Tensor shape(batch, pomo) contains customer index chosen by model
#     selected_route: Tensor shape(batch, pomo) contain route index chosen by model
#     Return:
#         new_routes // same as cur_routes, but is inserted selected customer into selected route
#         shape(batch, pomo, n, n)

#     '''
    
#     batch, pomo, _, n = cur_routes.shape
#     BATCH_IDX = torch.arange(batch)[:, None].expand(batch, pomo)
#     POMO_IDX = torch.arange(pomo)[None, : ].expand(batch, pomo)
#     raw_selected_route = selected_route.clone()
#     selected_route = selected_route.unsqueeze(-1)
#     node_num = torch.gather(truck_num, 2, selected_route)  # shape (batch, pomo, 1)
#     node_num = node_num - 1
#     selected_route = selected_route.unsqueeze(-1).expand(-1, -1, 1, n)
#     nodes_route = torch.gather(cur_routes, 2, selected_route).squeeze(2)
#     node_xy_expand = node_xy.unsqueeze(1).expand(-1, pomo, -1, -1)
#     raw_selected_node = selected_node.clone()
#     selected_node = selected_node.unsqueeze(-1).unsqueeze(-1).expand(-1, -1, 1, 2)
#     selected_node_coord = torch.gather(node_xy_expand, 2, selected_node)
#     nodes_route_expand = nodes_route.unsqueeze(-1).expand(-1, -1, -1, 2)
#     nodes_route_coords = torch.gather(node_xy_expand, 2, nodes_route_expand)  # shape (batch, pomo, n, 2)
#     node_num_expand = node_num.unsqueeze(-1).expand(-1, -1, -1, 2)  # shape(batch, pomo, 1, 2)
#     last_node_coord = torch.gather(nodes_route_coords, 2, node_num_expand)  # shape(batch, pomo,1, 2)
#     depot_expand = depot.unsqueeze(1).unsqueeze(1).expand(-1, pomo, 1, -1)
#     distance_lastnode_depot = torch.sqrt(torch.sum((last_node_coord - depot_expand) ** 2, dim=-1))
#     # shape(batch, pomo, 1)
#     distance_selected_depot = torch.sqrt(torch.sum((selected_node_coord - depot_expand) ** 2, dim=-1))
#     # shape(batch, pomo, 1)
#     distances = torch.sqrt(torch.sum((selected_node_coord - nodes_route_coords) ** 2, dim=-1))
#     # shape(batch, pomo, n)

#     range_tensor = torch.arange(n).unsqueeze(0).unsqueeze(0)  # Shape: (1, 1, n)

#     padding = range_tensor > node_num
#     padding = padding * 10  # shape (batch, pomo, n)
#     distances = distances + padding

#     new_distances = distances.clone()
#     new_distances = torch.concat((distance_selected_depot, new_distances), dim=2)  # shape (batch, pomo, n + 1)
#     node_num = node_num + 1
#     distances[BATCH_IDX, POMO_IDX, node_num.squeeze(2)] = distance_lastnode_depot
#     distance_lastnode_depot = distance_lastnode_depot * 10
#     distances = torch.concat((distances, distance_lastnode_depot), dim=2)  # shape (batch, pomo, n + 1)
#     inserted_cost = new_distances + distances  # shape (batch, pomo, n + 1)
#     insert_index = torch.argmin(inserted_cost, dim=2)  # shape (batch, pomo)
#     new_nodes_route = torch.zeros((batch, pomo, n + 1), dtype= torch.int64)
#     expanded_indices = torch.arange(n + 1).expand(batch, pomo, -1)  # Shape: (batch, n)
#     mask_before = expanded_indices < insert_index.unsqueeze(1)  # Shape: (batch, n+1)
#     mask_after = expanded_indices > insert_index.unsqueeze(1)
#     new_nodes_route[mask_before] = nodes_route[mask_before[:, :, :-1]]
#     new_nodes_route[mask_after] = nodes_route[mask_after[:, :, 1:]]
#     new_nodes_route[BATCH_IDX, POMO_IDX, insert_index] = raw_selected_node
#     cur_routes[BATCH_IDX, POMO_IDX, raw_selected_route] = new_nodes_route[:, :, :-1]
#     return cur_routes  # shape (batch, pomo, n, n)


# # # # Gọi hàm với dữ liệu giả và in kết quả
# new_routes = update_route(node_xy, depot, truck_num, cur_routes, selected_node, selected_route)
# print("New Routes:\n", new_routes)



# hàm tính khoảng cách
def compute_total_distance(node_xy, depot, index_sequence):
    """
    Tính tổng khoảng cách cho dãy các chỉ số và thêm khoảng cách từ depot đến điểm đầu tiên và từ điểm cuối đến depot.

    Args:
    - node_xy (Tensor): Các tọa độ của khách hàng, có kích thước (batch, n, 2).
    - depot (Tensor): Tọa độ của depot, có kích thước (batch, 1, 2).
    - index_sequence (Tensor): Dãy các chỉ số với kích thước (batch, m), m là số điểm trong dãy.

    Returns:
    - total_distance (Tensor): Tổng khoảng cách của dãy chỉ số với kích thước (batch, 1).
    """

    batch_size, num_points = index_sequence.shape  # batch_size: số batch, num_points: số điểm trong dãy
    total_distance = torch.zeros(batch_size, 1)  # Khởi tạo biến để tính tổng khoảng cách

    # Duyệt qua từng batch và tính tổng khoảng cách
    for b in range(batch_size):
        # Lấy dãy chỉ số của batch hiện tại
        indices = index_sequence[b]  # Dãy chỉ số (mảng có độ dài m)

        # Tính tổng khoảng cách giữa các điểm liên tiếp trong dãy chỉ số
        for i in range(1, len(indices)):
            start_idx = indices[i - 1]
            end_idx = indices[i]

            # Tính khoảng cách giữa các điểm trong dãy chỉ số
            total_distance[b] += torch.norm(node_xy[b, start_idx] - node_xy[b, end_idx], p=2)

        # Cộng khoảng cách từ depot đến điểm đầu tiên trong dãy
        first_node_idx = indices[0]
        total_distance[b] += torch.norm(depot[b] - node_xy[b, first_node_idx], p=2)

        # Cộng khoảng cách từ điểm cuối trong dãy về depot
        last_node_idx = indices[-1]
        total_distance[b] += torch.norm(depot[b] - node_xy[b, last_node_idx], p=2)

    return total_distance


if __name__ == "__main__":

    # m thử chèn lần lượt và xem kết quả so với cái new_routes


    index_sequence = torch.tensor([[0, 1, 4]])

    total_distance = compute_total_distance(node_xy, depot, index_sequence)

    print("Total Distance:", total_distance)
