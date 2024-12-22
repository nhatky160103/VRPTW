import torch



import torch


batch_size = 1  # Số lượng batch
pomo_size = 1   # Số lượng POMO
n = 4           # Số lượng nodes

# cur_demands: (batch, pomo, n)
cur_demands = torch.tensor([[[1.0, 2.0, 3.0, 4.0]]], dtype=torch.float)

# node_demand: (batch, n)
node_demand = torch.tensor([[1.0, 2.0, 3.0, 4.0]], dtype=torch.float)

# cur_mask: (batch, pomo, n, n)
cur_mask = torch.zeros(batch_size, pomo_size, n, n, dtype=torch.int64)

# max_demand: (batch)
max_demand = torch.tensor([6], dtype=torch.float32)

# selected_route: (batch, pomo, n)
selected_route = torch.tensor([[3]], dtype=torch.int64)

# Kiểm tra các tensor
print(f"cur_demands.shape: {cur_demands.shape}")
print(f"node_demand.shape: {node_demand.shape}")
print(f"cur_mask.shape: {cur_mask.shape}")
print(f"max_demand.shape: {max_demand.shape}")
print(f"selected_route.shape: {selected_route.shape}")





def update_demand_mask(cur_demands, node_demand, cur_mask, max_demand, selected_route):
    '''
        cur_demands Tensor shape (batch, pomo, n)
        node_demand Tensor shape (batch, n)
        cur_mask Tensor shape (batch, pomo, n, n) --> mask n-m route, n - 
        max_demand Tensor shape(batch)
    '''
    batch,pomo,n = cur_demands.shape
 
    BATCH_IDX = torch.arange(batch)[:, None].expand(batch, pomo)
    POMO_IDX = torch.arange(pomo)[None, :].expand(batch, pomo)
    selected_route_demand = torch.gather(cur_demands, 2, selected_route.unsqueeze(-1))
    node_demand = node_demand.unsqueeze(1).expand(-1, pomo, n)
    round_error_epsilon = 0.00001
    max_demand = max_demand.unsqueeze(-1).unsqueeze(-1)
    demand_mask = selected_route_demand + node_demand - round_error_epsilon > max_demand #shape(batch, pomo, n)
    cur_mask[BATCH_IDX, POMO_IDX, :,  selected_route] = torch.where(cur_mask[BATCH_IDX, POMO_IDX, :,  selected_route] == 0, demand_mask, 1)
    return cur_mask
 
new_cur_mask = update_demand_mask(cur_demands, node_demand, cur_mask, max_demand, selected_route)

print(new_cur_mask)