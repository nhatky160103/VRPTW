import os
from parallel_algorithm import parallel_algorithm
import pandas as pd
from main import create_data_model
from read_data import get_data
from gen_pop_greedy_new import nearest_neighbor


def create_report(num_test):
    data_path = 'Solomon_25'
    test_names = os.listdir(data_path)[: num_test]

    name_list = []
    solomon_solution = []
    solomon_cost = []
    parallel_solution = []
    parallel_cost = []
    solomon_nr = []
    parallel_nr= []

    for test_name in test_names:

        m, Q, D, e0, l0, cost_matrix, customers = get_data(test_name)
        final_routes = []

        routes, cost = nearest_neighbor(customers, m, Q, D, e0, l0, cost_matrix)
        if routes != -1:
            final_routes = []
            for route in routes:
                temp_route = []
                for customer in route:
                    temp_route.append(customer + 1)
                final_routes.append(temp_route)

        solution = []
        if len(final_routes) != 0:
            seed_route, my_customers = create_data_model(customers, final_routes, Q, D, e0, l0, cost_matrix)
            best_solution, nr_min, best_cost, best_param = parallel_algorithm(seed_route, cost_matrix, my_customers)
            for route in best_solution:
                temp_route = [customer.index for customer in route.customers]
                solution.append(temp_route)

            solomon_cost.append(cost)
            solomon_solution.append(final_routes)
            parallel_cost.append(best_cost)
            parallel_solution.append(solution)
            name_list.append(test_name)
            solomon_nr.append(len(final_routes))
            parallel_nr.append(len(solution))

    data = {
        'Test Name': name_list,  # Cột 1: Tên test
        'Solomon Solution': solomon_solution,  # Cột 2
        'Solomon num_route': solomon_nr,
        'Solomon Cost': solomon_cost,  # Cột 3: Kết quả cost
        'Parallel Solution': parallel_solution,  # Cột 4
        'Parallel num_route': parallel_nr,
        'Parallel Cost': parallel_cost  # Cột 5: Kết quả parallel

    }
    df = pd.DataFrame(data)

    excel_path = 'result.xlsx'
    df.to_excel(excel_path, index=False)

    print(f'Create exel file successfully ! ......:  {excel_path}')


if __name__ == "__main__":
    num_test = int(input('Input the number off test...: '))
    create_report(num_test)
