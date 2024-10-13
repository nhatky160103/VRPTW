from gen_pop_greedy_new import nearest_neighbor, Customer_Tu
from read_data import get_data
from build_route import Customer, Route, build_routes, distance_between
INF = 10000


def create_data_model(customers, routes, Q, D, e0, l0, cost_matrix):
    # đây chính là danh sách các khách hàng và route được lấy từ thuật toán sequence
    """
    :param routes: đây chính là list các route mà mỗi route là một list các khách hàng
    :return:
        seed_route: khởi tạo ban đầu của các route mỗi route chỉ bao gồm depot và khách haàng xa depot nhất của mỗi route
        customers: list tất cả các customer bao gồm cả depot
    """

    depot = Customer(0, 0, 0, e0, l0)
    depot.is_routed = True

    my_customers = [depot]

    for i, customer in enumerate(customers):
        temp_customer = Customer(i+1, customer.demand, customer.service_time, customer.time_window[0], customer.time_window[1])
        my_customers.append(temp_customer)

    seed_route = []
    for i, route in enumerate(routes):
        temp_route = Route(i, depot, Q, D)  # khởi tạo một route chỉ gồm depot
        optim_cost = -INF
        optim_customer = None

        # thực hiện tìm khách hàng xa depot nhất
        for index_customer in route:  # xét tất cả những khách hàng
            cost = distance_between(my_customers[index_customer], depot, cost_matrix)
            if cost > optim_cost:
                optim_cost = cost
                optim_customer = my_customers[index_customer]
        temp_route.insert_customer(optim_customer, 1, cost_matrix)  # thêm khách hàng xa nhất vào route đó
        seed_route.append(temp_route)  # thêm route vào seed_route

    return seed_route, my_customers


def print_routes(routes, cost_matrix, customers):
    for route in routes:
        load = 0
        result = f'[0] --{cost_matrix[0][route[0]]}--> '
        for i, customer in enumerate(route):
            load += customers[customer-1].demand
            result += f'{customers[customer-1].time_window}'
            result += f'[{customer}]'
            if i != len(route) - 1:
                result += f' --{cost_matrix[route[i]][route[i+1]]}-->'
        result += f'--{cost_matrix[route[-1]][0]}--> [0]'
        print(result + f" || total load: {load} ")


def print_routes2(routes, cost_matrix):
    print(f'Num route :{len(routes)}\n')

    for route in routes:
        load = 0
        result = f'[0] --{cost_matrix[0][route.customers[1].index]}--> '
        for i, customer in enumerate(route.customers):
            if i == 0:
                continue
            load += customer.q
            result += f'{customer.e, customer.l}'
            result += f'[{customer.index}]'
            if i != len(route.customers) - 1:
                result += f' --{cost_matrix[route.customers[i].index][route.customers[i+1].index]}-->'  # Chi phí giữa các khách hàng
        result += f'--{cost_matrix[route.customers[-1].index][0]}--> [0]'  # Trở về điểm gốc 0
        print(result + f"   |___total load:{load}___|___Total time:{route.time}___|")

    print('FINISH')

    load = 0
    for route in routes:
        load += route.load

    cost = 0
    for route in routes:
        cost += route.time
    print("TOTAL COST:", cost)
    print("TOTAL LOAD:", load)

def print_routes3(routes):
    for route in routes:
        print([customer.index for customer in route.customers])


if __name__ == "__main__":
    test_case = input('Input the test case: ... ')  # input the name of folder in the input dir
    m, Q, D, e0, l0,  cost_matrix, customers = get_data(test_case)
    final_routes = []

    routes, cost = nearest_neighbor(customers, m, Q, D, e0, l0, cost_matrix)
    if routes != -1:
        final_routes = []
        for route in routes:
            temp_route = []
            for customer in route:
                temp_route.append(customer+1)
            final_routes.append(temp_route)

        print("____"*20)
        print("final_route greedy algorithm:\n")
        print_routes(final_routes, cost_matrix, customers)
        print(cost)
        print("____"*20)

    if len(final_routes) != 0:
        alpha_param = [(1, 0), (0.5, 0.5), (0.75, 0.25)]

        for alpha in alpha_param:
            print(f'Param {alpha}')
            seed_route, my_customers = create_data_model(customers, final_routes, Q, D, e0, l0, cost_matrix)
            nr = len(seed_route)
            print('seed:')
            print_routes3(seed_route)
            print("____" * 20)
            print('customers: ')
            print('|'.join(f"{cus.index}: {cus.is_routed}" for cus in my_customers))
            best_solution = build_routes(nr, seed_route, cost_matrix, my_customers, alpha[0], alpha[1])

            if best_solution:
                print("____"*20)
                print(f"final solution of build_route of {alpha}:\n")
                print_routes2(best_solution, cost_matrix)
                print("____" * 20)









