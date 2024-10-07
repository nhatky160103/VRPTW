#### READ INPUT #####
import os
from gen_pop_greedy_new import Customer_Tu
alpha = beta = 0.5

def get_data(test_case):

    data_path = os.path.join('input_dir', test_case, 'data_infor.txt')
    customer_path = os.path.join('input_dir', test_case, 'customer_data.txt')
    matrix_path = os.path.join('input_dir', test_case, 'cost_matrix.txt')

    with open(data_path, mode ="r") as datainfo_file:
        data_infos = datainfo_file.readlines()
    m, Q, D, e0, l0 = [int(float(c)) for c in data_infos[0].split()]

    with open(customer_path, mode="r") as customerinfo_file:
        customers_info = customerinfo_file.readlines()

    customers = []
    for i in range(len(customers_info)):

        idxi, qi,  si, ei, li = [int(float(c)) for c in customers_info[i].split()]
        customers.append(Customer_Tu(qi, si, (ei, li)))

    with open(matrix_path, "r") as cost_file:
        cost_data = cost_file.readlines()

    cost_matrix = []
    for row in cost_data:
        row = [float(c) for c in row.split()]
        cost_matrix.append(row)

    return m, Q, D, e0, l0, cost_matrix, customers


if __name__ =="__main__":
    test_case = input('Input the testcase: ... ')

    m, Q, D, e0, l0, cost_matrix, customers = get_data(test_case)
    print(cost_matrix)
    for customer in customers:
        print(customer.demand, customer.service_time, customer.time_window)
    print(m, Q, D, e0, l0)

