
import matplotlib.pyplot as plt
import networkx as nx
import time
import math
import copy


depot = {'x': 0.1, 'y': 0.5}  # Tọa độ Depot

input_nodes = [
    {'id': 1, 'x': 0.2,  'y': 0.3, 'demand': 5},
    {'id': 2, 'x': 0.5,  'y': 0.35, 'demand': 5},
    {'id': 3, 'x': 0.7,  'y': 0.15, 'demand': 5},
    {'id': 4, 'x': 0.6,  'y': 0.5, 'demand': 5},
    {'id': 5, 'x': 0.3,  'y': 0.1, 'demand': 5},
    {'id': 6, 'x': 0.4,  'y': 0.25, 'demand': 5},
    {'id': 7, 'x': 0.15, 'y': 0.5, 'demand': 5},
    {'id': 8, 'x': 0.7,   'y': 0.4, 'demand': 5},
    {'id': 9, 'x': 0.55,  'y': 0.1, 'demand': 5},
    {'id': 10, 'x': 0.35, 'y': 0.4, 'demand': 5},
    {'id': 11, 'x': 0.6, 'y': 0.15, 'demand': 5},
    {'id': 12, 'x': 0.8, 'y': 0.25, 'demand': 5},
    {'id': 13, 'x': 0.2, 'y': 0.15, 'demand': 5},
    {'id': 14, 'x': 0.3, 'y': 0.15, 'demand': 5},
    {'id': 15, 'x': 0.4, 'y': 0.15, 'demand': 5},
    {'id': 16, 'x': 0.5, 'y': 0.15, 'demand': 5},
    {'id': 17, 'x': 0.6, 'y': 0.15, 'demand': 5},
    {'id': 18, 'x': 0.7, 'y': 0.15, 'demand': 5},
] 


# Dữ liệu đầu vào
decode_input_paper = [

    {'position': 2, 'node_idx': 7,  'route_idx': 0},
    {'position': 3, 'node_idx': 6,  'route_idx': 0},
    {'position': 4, 'node_idx': 5, 'route_idx': 0},
    {'position': 5, 'node_idx': 0,  'route_idx': 0},


    {'position': 2, 'node_idx': 16, 'route_idx': 1},
    {'position': 3, 'node_idx': 15, 'route_idx': 1},
    {'position': 4, 'node_idx': 14, 'route_idx': 1},
    {'position': 5, 'node_idx': 17, 'route_idx': 1},
    {'position': 6, 'node_idx': 0,  'route_idx': 1},


    {'position': 2, 'node_idx': 8,  'route_idx': 2},
    {'position': 3, 'node_idx': 9,  'route_idx': 2},
    {'position': 4, 'node_idx': 10, 'route_idx': 2},
    {'position': 5, 'node_idx': 0, 'route_idx': 2},

    {'position': 2, 'node_idx': 11,  'route_idx': 3},
    {'position': 3, 'node_idx': 12,  'route_idx': 3},
    {'position': 4, 'node_idx': 13, 'route_idx': 3},
    {'position': 5, 'node_idx': 0, 'route_idx': 3},
]



decode_input_outmethod = [
    {'position': 2, 'node_idx': 16, 'route_idx': 1},
    {'position': 3, 'node_idx': 15, 'route_idx': 1},
    {'position': 3, 'node_idx': 6,  'route_idx': 0},
    {'position': 4, 'node_idx': 14, 'route_idx': 1},
    {'position': 2, 'node_idx': 17, 'route_idx': 1},
    {'position': 2, 'node_idx': 7,  'route_idx': 0},
    {'position': 4, 'node_idx': 5, 'route_idx': 0},
    {'position': 2, 'node_idx': 8,  'route_idx': 2},
    {'position': 3, 'node_idx': 9,  'route_idx': 2},
    {'position': 3, 'node_idx': 12,  'route_idx': 3},
    {'position': 4, 'node_idx': 10, 'route_idx': 2},
    {'position': 2, 'node_idx': 11,  'route_idx': 3},
    {'position': 4, 'node_idx': 13, 'route_idx': 3},


    {'position': 6, 'node_idx': 0,  'route_idx': 1},
    {'position': 5, 'node_idx': 0,  'route_idx': 0},
    {'position': 5, 'node_idx': 0, 'route_idx': 2},
    {'position': 5, 'node_idx': 0, 'route_idx': 3},
]

save_route = [[0, 1], [0, 2], [0, 3], [0, 4]]


def distance(a, b):
    return math.sqrt((a['x'] - b['x']) ** 2 + (a['y']-b['y'])**2)


def calculate_cost(route):
    cost = 0
    for i in range(len(route)-1):
        
        node_a = input_nodes[route[i] - 1]  
        node_b = input_nodes[route[i + 1] - 1]

        if i ==0:
            node_a = depot

        if route[i+1] == 0:
            node_b = depot
        cost += distance(node_a, node_b)


    return cost

# Hàm tính tổng yêu cầu (load) của route
def calculate_load(route):
    load = 0

    for i , node_idx in enumerate(route):
        if i == 0 or node_idx==0:
            continue
        load += input_nodes[node_idx - 1]['demand'] 
    return load


def display_routes(save_route, decode_input1, decode_input2):
    save_route1 = copy.deepcopy(save_route)
    save_route2 = copy.deepcopy(save_route)
    total_cost1 = 0
    total_cost2 = 0
    plt.ion()  # Bật chế độ tương tác
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))  

    # Hàm để vẽ đồ thị
    def draw_graph(ax, action, save_route, highlight_route_idx=None):
        ax.clear()
        x_offset = 0  # Tọa độ x ban đầu

        total_cost = 0

        for route_idx, route in enumerate(save_route):
            y = -route_idx  # Mỗi route nằm trên một dòng

            for i, node in enumerate(route):
                ax.plot([x_offset + i], [y], 'o', color='red' if node == action.get('node_idx', -1) else 'blue', markersize=20)
                ax.text(x_offset + i, y, str(node), fontsize=10, ha='center', va='center', color='white')

            if len(route) > 1:
                for i in range(len(route) - 1):
                    ax.plot([x_offset + i + 0.2, x_offset + i + 0.8], [y, y], color='gray', linestyle='--')


            ax.text(-2, y+0.1, f"Route {route_idx}", fontsize=10, fontweight='bold', color='#2C3E50', ha='right')  # Tô đậm, màu tối

            # Hiển thị tổng chi phí và load với màu sắc chuyên nghiệp
            cost = calculate_cost(route)
            total_cost += cost 
            load = calculate_load(route)
            ax.text(-2, y - 0.2, f"Cost: {cost:.2f}", fontsize=8, fontweight='bold', color='#E74C3C', ha='right')  # Màu đỏ cho cost
            ax.text(-2, y - 0.45, f"Load: {load}", fontsize=8, fontweight='bold', color='#3498DB', ha='right')  # Màu xanh cho load

            # Vẽ khung nét đứt bao quanh route được highlight
            if highlight_route_idx == route_idx:
                x_min = x_offset - 0.5
                x_max = x_offset + len(route) - 0.5
                y_min = y - 0.5
                y_max = y + 0.5
                ax.add_patch(plt.Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, 
                                           edgecolor='gray', linestyle='--', linewidth=1, facecolor='none',alpha=0.3))
        print("__"*20)
        ax.set_xlim(-2, max(len(route) for route in save_route) + 2)
        ax.set_ylim(-len(save_route), 1)
        ax.axis('off')

        return total_cost


    for  action1, action2 in zip(decode_input1, decode_input2):
        position1 = action1['position']
        node_idx1 = action1['node_idx']
        route_idx1 = action1['route_idx']

        route1 = save_route1[route_idx1]
        route1.insert(position1, node_idx1)


        position2 = action2['position']
        node_idx2 = action2['node_idx']
        route_idx2 = action2['route_idx']

        route2 = save_route2[route_idx2]
        route2.insert(position2, node_idx2)


        # Vẽ đồ thị lên subplot 1 và subplot 2
        total_cost1 = draw_graph(ax1,action1,save_route1, highlight_route_idx=route_idx1)
        total_cost2 = draw_graph(ax2,action2,save_route2, highlight_route_idx=route_idx2)
        
        ax1.set_title(f"Paper method Add Node {node_idx1} to Route {route_idx1} | Total cost: {total_cost1:.2f} ")
        ax2.set_title(f"Out method Add Node {node_idx2} to Route {route_idx2} | Total cost: {total_cost2:.2f} ")
        plt.pause(1.5)

    plt.ioff()  # Tắt chế độ tương tác
    plt.show()


# Gọi hàm để hiển thị
display_routes(save_route, decode_input_paper, decode_input_outmethod)