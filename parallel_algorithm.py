import itertools
from build_route import build_routes, distance_between
from gen_pop_greedy_new import nearest_neighbor
from read_data import get_data
from main import create_data_model
from main import print_routes, print_routes2, print_routes3
import copy
INF = 100000


def find_s_star(seed_route, cost_matrix):

    """
    :param seed_route: seed khởi tạo ban đầu (đây là list các route mỗi route chỉ bao gồm 2 điểm là depot và seed customer)
    :param cost_matrix: ma trận chi phí
    :return: trả về route cần loại trong một seed
    """
    s_star= None
    min_dist= INF
    for route1 in seed_route:
        for route2 in seed_route:
            if route1.index != route2.index:
                cost = distance_between(route1.customers[-1], route2.customers[-1], cost_matrix)
                if cost < min_dist:
                    min_dist = cost
                    s_star = route1

    return s_star


def cal_cost(solution):
    cost = 0
    for route in solution:
        cost += route.time
    return cost


def parallel_algorithm(seed_route, cost_matrix, my_customers):

    best_solution = None
    nr_min = None
    best_cost = INF
    best_param = None

    alpha_param = [(1, 0), (0.5, 0.5), (0.75, 0.25)]
    nr = len(seed_route)
    for alpha in alpha_param:
        print("alpha", alpha)
        temp_seed = copy.deepcopy(seed_route)
        temp_my_customers = copy.deepcopy(my_customers)
        for i in range(nr, 1, -1):
            print('r: ', i)
            print_routes3(temp_seed)
            seed_route_copy = copy.deepcopy(temp_seed)
            my_customers_copy = copy.deepcopy(temp_my_customers)
            solution = build_routes(i, seed_route_copy, cost_matrix, my_customers_copy, alpha[0], alpha[1])

            if not solution:
                break
            else:

                s_star = find_s_star(temp_seed, cost_matrix)
                for customer in temp_my_customers:  # gán lại giá trị is_routes cho các khách hàng bị loại ra khỏi seed_route
                    if customer.index == s_star.customers[-1].index:
                        customer.is_routed = False

                temp_seed = [route for route in temp_seed if route.index != s_star.index]

                cost = cal_cost(solution)
                print('cost: ', cost)
                if cost < best_cost:
                    best_cost = cost
                    nr_min = i
                    best_solution = solution
                    best_param = alpha

    return best_solution, nr_min, best_cost, best_param

if __name__ == '__main__':

    test_case = input('Input the test case: ... ')  # input the name of folder in the input dir
    m, Q, D, e0, l0, cost_matrix, customers = get_data(test_case)
    final_routes = []

    routes, cost = nearest_neighbor(customers, m, Q, D, e0, l0, cost_matrix)
    if routes != -1:
        final_routes = []
        for route in routes:
            temp_route = []
            for customer in route:
                temp_route.append(customer + 1)
            final_routes.append(temp_route)

        print("____" * 20)
        print("final_route greedy algorithm:\n")
        print_routes(final_routes, cost_matrix, customers)
        print(cost)
        print("____" * 20)

    if len(final_routes) != 0:
        alpha_param = [(1, 0), (0.5, 0.5), (0.75, 0.25)]

        seed_route, my_customers = create_data_model(customers, final_routes, Q, D, e0, l0, cost_matrix)
        nr = len(seed_route)
        print("____" * 20)


        for alpha in alpha_param:
            seed_route, my_customers = create_data_model(customers, final_routes, Q, D, e0, l0, cost_matrix)
            nr = len(seed_route)
            print(f'Param {alpha}')
            print('seed:')
            print_routes3(seed_route)
            print("____" * 20)
            print('customers: ')
            print('|'.join(f"{cus.index}: {cus.is_routed}" for cus in my_customers))

            best_solution = build_routes(nr, seed_route, cost_matrix, my_customers, alpha[0], alpha[1])


            if best_solution:
                print("____" * 20)
                print(f"final solution of build_route of {alpha}:\n")
                print_routes2(best_solution, cost_matrix)
                print("____" * 20)


