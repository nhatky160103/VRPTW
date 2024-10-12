import numpy as np
INF = 10000


class Customer:
    def __init__(self, index, q=None, s=None,  e=None, l=None):
        self.index = index
        self.q = q  # Khối lượng hàng hóa
        self.s = s  # Thời gian phục vụ
        self.e = e  # Thời gian bắt đầu
        self.l = l  # Thời gian hoàn thành
        self.is_routed = False
        self.finish_serve_time = 0


class Route:
    def __init__(self,index, depot_location, max_load, max_time):
        self.customers = [depot_location]  # Khởi tạo với kho
        self.depot_location = depot_location
        self.index = index
        self.load = 0
        self.time = 0
        self.max_load = max_load
        self.max_time = max_time

    def insert_customer(self, new_customer, index, cost_matrix):
        new_customer.is_routed = True
        self.customers.insert(index, new_customer)

        for i in range(index, len(self.customers)):
          self.customers[i].finish_serve_time = calc_b(self.customers[i-1], self.customers[i], cost_matrix)

        self.time = self.customers[-1].finish_serve_time - self.customers[0].e + distance_between(self.customers[-1], self.customers[0], cost_matrix)
        self.load += new_customer.q


def distance_between(c1, c2, cost_matrix):
    return cost_matrix[c1.index][c2.index]


def calc_b(prev_customer, customer, cost_matrix):# tính thời gian hoàn thành việc phục vụ cho một khách hàng với điều kiện đã biết được thời gian phục vụ của khách hàng trước đó
    if prev_customer is None or customer is None:
        return INF
    return max(customer.e, prev_customer.finish_serve_time + distance_between(prev_customer, customer, cost_matrix)) + customer.s


def calc_c1(prev_customer, new_customer, next_customer, cost_matrix, a1,  a2):

    detour = (distance_between(prev_customer, new_customer, cost_matrix) # detour phản ánh mức độ lệch tổng chi phí trước và sau khi thêm khách hàng u
    + distance_between(new_customer, next_customer, cost_matrix) - distance_between(prev_customer, next_customer, cost_matrix))

    bj = calc_b(prev_customer, next_customer, cost_matrix)# thời gian hoàn thành phục vụ của next_customer trước khi thêm u

    bu = calc_b(prev_customer, new_customer, cost_matrix) # thời gian hoàn thành phục vụ của new_customer

    buj = max(next_customer.e, bu + distance_between(new_customer, next_customer, cost_matrix)) + next_customer.s # thời gian hoàn thành của next_customer sau khi đã thêm u vào

    delay = buj - bj # thể hiện độ trễ khi thêm u vào

    return a1 * detour + a2 * delay


def insertion_cost(route, new_customer, a1, a2, cost_matrix):
    min_cost = INF
    best_position = -1

    for i in range(1, len(route.customers)): # bắt đầu chèn từ vị trí sau vị trí 0 (không thể chèn trước depot được)
        if check_feasible(route, new_customer, i, cost_matrix):
            if i == len(route.customers):  # Chèn ở cuối lộ trình
                cost = calc_c1(route.customers[-1], new_customer, route.customers[0], cost_matrix, a1,  a2)

            else:  # Chèn giữa các khách hàng
                cost = calc_c1(route.customers[i - 1], new_customer, route.customers[i], cost_matrix, a1, a2)

            if cost < min_cost:
                min_cost = cost
                best_position = i

    return min_cost, best_position # đây là vị trí điểm j tức là cần chèn khách vào trước điểm này là phương án tốt nhất



def calc_c2(list_index, customer, routes, cost_matrix, a1, a2):

    total_cost = 0
    optim_cost = INF

    for i, route in enumerate(routes): # duyệt qua từng route thực hiện tính c1 đối với mỗi route
        if list_index[i] != -1:
            prev_customer = route.customers[list_index[i]-1]
            next_customer = route.customers[list_index[i]]
            cost = calc_c1(prev_customer,  customer, next_customer, cost_matrix, a1, a2)
        else:
            cost = INF
        total_cost += cost
        if cost < optim_cost:
          optim_cost = cost

    return total_cost - len(routes)*optim_cost  # là tổng cost của các route không tối ưu trừ cost của route tối ưu



import copy

def check_feasible(route, new_customer, position, cost_matrix):

    temp_route = copy.deepcopy(route)
    temp_route.insert_customer(new_customer, position, cost_matrix)

    if route.load + new_customer.q > route.max_load or temp_route.time > route.max_time :
        return False

    for i in range(position, len(temp_route.customers)):
        arrive_time = temp_route.customers[i-1].finish_serve_time + distance_between(temp_route.customers[i-1], temp_route.customers[i], cost_matrix)
        due_time = temp_route.customers[i].l
        if arrive_time > due_time:
             # nếu thời gian đến mà sau duetime thì không thỏa mãn
             return False

    return True



def build_routes( nr, routes, cost_matrix, all_customer, a1, a2):

    """
    args:
    today_customers: là list các đối tượng Customer, chứa depot ở vị trí 0
    nr: số lượng route được tạo ra từ thuật toán sequence
    routes: là mảng các đối tượng Route, mỗi đối tượng chỉ chứa depot(0) và customer xa depot nhất
    cost_matrix: chỉ bao gồm chi phí giữa các customer hôm nay và depot

    return:
    solution_routs: là mảng các route đã được sắp xếp theo chi phí tốt nhất
    """

    remaining_customer = [customer for customer in all_customer if not customer.is_routed]

    while remaining_customer:

        # tính ma trận index tốt nhất
        index_matrix = {}  # một map mới key là khách hàng và giá trị là list các index mỗi index là vị trí tốt nhất đối với từng route

        for customer in remaining_customer:# duyệt qua từng khách hàng
          for route in routes: # thực hiện tính vị trí chèn đối với từng route
            cost, index = insertion_cost(route, customer, a1, a2, cost_matrix)
            if customer not in index_matrix:
              index_matrix[customer] = []
            index_matrix[customer].append(index)

        # thực hiện tìm ra u* khách hàng tối ưu nhất
        optimal_c2 = -INF
        optimal_customer = None

        for customer in remaining_customer:
          c2_cost = calc_c2(index_matrix[customer], customer, routes, cost_matrix, a1, a2)
          if c2_cost > optimal_c2:
            optimal_c2 = c2_cost
            optimal_customer = customer

        # thực hiện tìm ra route tốt nhất đối với u*
        optim_cost = INF

        optim_position = None
        optim_route_index = -1


        for i, route in enumerate(routes):
          cost , index = insertion_cost(route, optimal_customer, a1, a2, cost_matrix)
          if cost < optim_cost:
            optim_cost = cost
            optim_position = index
            optim_route_index = i

        if optim_position == None or optim_route_index ==None or optim_route_index == -1:
            print('NIL')
            return None
        elif check_feasible(routes[optim_route_index], optimal_customer, optim_position, cost_matrix) :
          optimal_customer.is_routed = True
          routes[optim_route_index].insert_customer(optimal_customer, optim_position, cost_matrix )
          remaining_customer.remove(optimal_customer)

        else:
          print('NIL')
          return None

    return routes