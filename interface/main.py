import pygame
import time
import math
import random


pygame.init()

screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Vehicle Route Animation")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)



# Danh sách màu cho từng xe
vehicle_colors = [RED, BLUE, GREEN]


depot = {'x': 0.1, 'y': 0.5}  # Tọa độ Depot



input_nodes = [
    {'id': 1, 'x': 0.2, 'y': 0.3, 'demand': 5},
    {'id': 2, 'x': 0.5, 'y': 0.35, 'demand': 3},
    {'id': 3, 'x': 0.7, 'y': 0.15, 'demand': 2},
    {'id': 4, 'x': 0.6, 'y': 0.5, 'demand': 4},
    {'id': 5, 'x': 0.3, 'y': 0.1, 'demand': 3},
    {'id': 6, 'x': 0.4, 'y': 0.25, 'demand': 2},
    {'id': 7, 'x': 0.15, 'y': 0.5, 'demand': 1},
    {'id': 8, 'x': 0.7, 'y': 0.4, 'demand': 4},
    {'id': 9, 'x': 0.55, 'y': 0.1, 'demand': 2},
    {'id': 10, 'x': 0.35, 'y': 0.4, 'demand': 3},
    {'id': 11, 'x': 0.6, 'y': 0.15, 'demand': 1},
    {'id': 12, 'x': 0.8, 'y': 0.25, 'demand': 5},
] 


decode_input = [
    {'position': 2, 'node_idx': 6, 'route_idx': 1},
    {'position': 3, 'node_idx': 7, 'route_idx': 1},
    {'position': 4, 'node_idx': 8, 'route_idx': 1},
    {'position': 2, 'node_idx': 9, 'route_idx': 1},

    {'position': 2, 'node_idx': 3,  'route_idx': 0},
    {'position': 3, 'node_idx': 4,  'route_idx': 0},
    {'position': 4, 'node_idx': 5, 'route_idx': 0},


]

save_route= [[0, 1], [0, 2]]

num_route = len(save_route)

def scale_nodes_to_screen(nodes, screen_width, screen_height):
    # Chuyển đổi các tọa độ x và y từ khoảng 0-1 sang tọa độ màn hình
    scaled_nodes = []
    for node in nodes:
        screen_x = int(node['x'] * screen_width)  # Nhân tọa độ x với chiều rộng màn hình
        screen_y = int(node['y'] * screen_height)  # Nhân tọa độ y với chiều cao màn hình
        
        # Cập nhật tọa độ mới
        scaled_nodes.append({
            'id': node['id'],
            'x': screen_x,
            'y': screen_y,
            'demand': node['demand']
        })
    return scaled_nodes


nodes = scale_nodes_to_screen(input_nodes, screen_width, screen_height)


depot_image = pygame.image.load('interface/depot.png')  # Tải ảnh Depot
depot_image = pygame.transform.smoothscale(depot_image, (30, 30)) 

depot_width, depot_height = depot_image.get_size()  # Lấy kích thước của ảnh

node_image = pygame.image.load('interface/node_icon.png')  # Tải ảnh Node
node_image = pygame.transform.smoothscale(node_image, (30, 30))  # Resize ảnh Node với smoothscale


background_image = pygame.image.load('interface/map.png')  # Thay 'path_to_your_map_image.png' bằng đường dẫn đến ảnh bản đồ
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))  # Resize ảnh theo kích thước cửa sổ


vehicle_image = pygame.image.load('interface/truck.png')  # Tải ảnh xe
vehicle_image = pygame.transform.scale(vehicle_image, (40, 40)) 




# Vẽ các node và Depot (cập nhật với ảnh Depot)
def draw_nodes():
    screen.blit(background_image, (0, 0))
    
    # Vẽ Depot dưới dạng ảnh
    screen.blit(depot_image, (depot['x'] - depot_width // 2, depot['y'] - depot_height // 2))  # Vẽ Depot ảnh, căn giữa

    for node in nodes:

        node_rect = node_image.get_rect(center=(node['x'], node['y']))
        screen.blit(node_image, node_rect)  # Vẽ ảnh node tại vị trí của node
        font = pygame.font.SysFont(None, 18 )

        info_text = f"ID: {node['id']}, D: {node['demand']}"
        text_x = node['x'] + 20  
        text_y = node['y'] - 10  
        
        text_surface = font.render(info_text, True, (255, 255, 255), 1)  # Text màu trắng
        screen.blit(text_surface, (text_x, text_y))


# Hàm tính khoảng cách Euclidean giữa hai điểm
def euclidean_distance(node_a, node_b):
    return math.sqrt((node_a['x'] - node_b['x'])**2 + (node_a['y'] - node_b['y'])**2)


traveled_routes = [[] for _ in range(num_route)]

# Di chuyển xe từ từ
def move_vehicle(route_idx, route, vehicle_color, poisition):
    
    vehicle_pos = [depot['x'], depot['y']]
    if poisition != -1:
        vehicle_pos = [nodes[route[poisition-1]]['x'],nodes[poisition-1]['y']]  # Bắt đầu từ Depot
    speed = 1000  # Tốc độ di chuyển (số pixel mỗi giây)

    current_node_idx = route[poisition-1]
    next_node_idx = route[poisition]
    
    current_node = depot if current_node_idx == 0 else nodes[current_node_idx - 1]
    next_node = depot if next_node_idx == 0 else nodes[next_node_idx - 1]
    
    # Tính toán khoảng cách giữa hai node
    distance = euclidean_distance(current_node, next_node)
    time_to_travel = distance / speed  # Thời gian để đi hết đoạn đường (s)
    
    # Tính toán di chuyển từ current_node đến next_node
    num_steps = int(time_to_travel * 60)  # Số bước di chuyển (60 fps)

    print('trước')

    for cus in  traveled_routes[route_idx]:
        print(f'{cus[0]['id']}', end=" ")
    
    print('\n')

    print('position', poisition)
    print('len(route) -1: ', len(route) -1 )
    if poisition != len(route) -1:
        num_node_deleted = len(route) - poisition
        traveled_routes[route_idx] =   traveled_routes[route_idx][: len(route)-num_node_deleted] 
        print('len:', len( traveled_routes[route_idx][: len(route)-num_node_deleted] ))
    print('sau')

    for cus in  traveled_routes[route_idx]:
        print(f'{cus[0]['id']}', end=" ")
          
    print('__________________________________________________________\n')


    for step in range(num_steps):
        t = step / num_steps  # Tỷ lệ thời gian giữa hai node
        vehicle_pos[0] = (1 - t) * current_node['x'] + t * next_node['x']
        vehicle_pos[1] = (1 - t) * current_node['y'] + t * next_node['y']

        # Vẽ lại màn hình
        draw_nodes()

        # Vẽ các đoạn đường đã đi qua của xe

        for i in range(num_route):
            for start_node, end_node, color in traveled_routes[i]:
                if i != route_idx:
                    color= CYAN
                pygame.draw.line(screen, color, (start_node['x'], start_node['y']), (end_node['x'], end_node['y']), 1)
          
            # Vẽ đoạn đường đang đi qua
            pygame.draw.line(screen, vehicle_color, (current_node['x'], current_node['y']), (vehicle_pos[0], vehicle_pos[1]), 1)

            vehicle_rect = vehicle_image.get_rect(center=(int(vehicle_pos[0]), int(vehicle_pos[1])))
            screen.blit(vehicle_image, vehicle_rect)
            pygame.display.update()

            time.sleep(1 / 120)  # Giới hạn fps ở 60 để di chuyển mượt mà

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

    # Lưu đoạn đường đã đi qua vào danh sách với màu xe tương ứng
    traveled_routes[route_idx].append((current_node, next_node, vehicle_color))
    
    pygame.display.update() 


def animate_multiple_vehicles():
    route_status = [0 for i in range(num_route)]
    for state in decode_input:
        print('state', state)
        route_index = state['route_idx']
        route_status[route_index] = 1
        save_route[route_index].insert(state['position'], state['node_idx'])

        move_vehicle(route_index, save_route[route_index], vehicle_colors[route_index], state['position'])
        time.sleep(0.5)


    time.sleep(5)  

animate_multiple_vehicles()



# Chờ cho đến khi người dùng đóng cửa sổ
pygame.time.wait(1000)  # Chờ 3 giây sau khi kết thúc animation
pygame.quit()

