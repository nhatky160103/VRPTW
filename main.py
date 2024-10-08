from gen_pop_greedy_new import nearest_neighbor, Customer_Tu
from read_data import get_data
from build_route import Customer, Route, build_routes, distance_between
from or_tools import get_routes

def create_data_model(customers, routes):
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


    seed_route= []
    for i, route in enumerate(routes):
        temp_route = Route(i, depot, Q, D) # khởi tạo một route chỉ gồm depot
        optim_cost= float('-inf')
        optim_customer = None

        # thực hiện tìm khách hàng xa depot nhất
        for index_customer in route: # xét tất cả những khách hàng
            cost = distance_between(my_customers[index_customer], depot, cost_matrix)
            if cost > optim_cost:
                optim_cost = cost
                optim_customer = my_customers[index_customer]
        temp_route.insert_customer(optim_customer, 1, cost_matrix) # thêm khách hàng xa nhất vào route đó
        seed_route.append(temp_route) # thêm route vào seed_route

    return seed_route, my_customers


def print_routes(routes):
    for route in routes:
        print([customer.index for customer in route.customers])


if __name__ == "__main__":
    test_case = input('Input the test case: ... ')  # input the name of folder in the input dir
    m, Q, D, e0, l0,  cost_matrix, customers = get_data(test_case)

    mode = int(input('select init mode: 1 for sequence and 2 for ortools: '))

    final_routes = []
    if mode == 1:
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
            print(final_routes)
            print(cost)
            print("____"*20)

    else:
        final_routes = get_routes(test_case)

    if len(final_routes) != 0:
        alpha_param = [(1, 0), (0.5, 0.5), (0.75, 0.25)]
        seed_route, my_customers = create_data_model(customers, final_routes)
        nr = len(seed_route)
        print("____" * 20)
        print('seed_route of build_route')
        print_routes(seed_route)
        print("____" * 20)

        for alpha in alpha_param:

            best_solution = build_routes(nr, seed_route, cost_matrix, my_customers, alpha[0], alpha[1])

            if best_solution:
                print("____"*20)
                print(f"final solution of build_route of {alpha}:\n")

                print_routes(best_solution)

                best_cost = 0
                for route in best_solution:
                    best_cost += route.time
                print(best_cost)
                print("____" * 20)









