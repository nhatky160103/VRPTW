class Customer_Tu:
    def __init__(self, demand, service_time, time_window):
        self.demand = demand # q
        self.service_time = service_time # s
        self.time_window = time_window # (ei, li)

class Route_Tu:
    def __init__(self):
        self.customers = []
        self.current_capacity = 0
        self.current_duration = 0

def nearest_neighbor(customers, m, Q, D, e0, l0, timecost_matrix):
    COST = 0
    n = len(customers)

    unrouted_customers = set(range(n))
    routes = []

    # each route
    for vehicle in range(m):

        print(f'>>>>> Unrouted customers for route {vehicle}: {unrouted_customers}')

        # if no more customers left today
        if not unrouted_customers:
            break

        route = Route_Tu()
        current_time = e0
        last_customer_index = -1
        nearest_customer = -1
        delays = []
        
        while True:

            best_cost = float('inf') #duong vc
            for j in unrouted_customers:
                if is_feasible(route, j, current_time, customers, Q, D, e0, l0, timecost_matrix):

                    costt = customers[j].time_window[1] - max(current_time + timecost_matrix[last_customer_index + 1][j + 1], customers[j].time_window[0])

                    cost = 0.5 * timecost_matrix[j + 1][0] + \
                        0.5 * (costt)

                    if cost < best_cost:
                        best_cost = cost
                        nearest_customer = j

            print(f'Nearest: {nearest_customer}')
            
            if nearest_customer == -1 or nearest_customer not in unrouted_customers:
                current_time += timecost_matrix[last_customer_index + 1][0]

                while current_time > l0 or current_time > D + e0:
                    if len(route.customers) > 1:
                        current_time = current_time - timecost_matrix[route.customers[-1] + 1][0] - customers[route.customers[-1]].service_time - delays[-1] - timecost_matrix[route.customers[-1] + 1][route.customers[-2] + 1]
                    else:
                        current_time = current_time - timecost_matrix[route.customers[-1] + 1][0] - customers[route.customers[-1]].service_time - delays[-1] - timecost_matrix[route.customers[-1] + 1][0]
                    
                    print(f"Remove customer {route.customers[-1]}")
                    unrouted_customers.add(route.customers[-1])
                    route.customers.pop()
                    delays.pop()

                    if route.customers != []:
                        current_time += timecost_matrix[route.customers[-1] + 1][0]
                    else:
                        break
                
                if route.customers != []:
                    COST += current_time
                    print(f'End route!')
                    print()
                    break
                else:
                    print('No more available customers!')
                    print()
                    return -1, -1
            
            route.customers.append(nearest_customer)
            route.current_capacity += customers[nearest_customer].demand
            route.current_duration += customers[nearest_customer].service_time

            delay = max(0, customers[nearest_customer].time_window[0] - current_time - timecost_matrix[last_customer_index + 1][nearest_customer + 1])
            delays.append(delay)

            current_time = max(customers[nearest_customer].time_window[0], timecost_matrix[last_customer_index + 1][nearest_customer + 1] + current_time) + customers[nearest_customer].service_time

            last_customer_index = nearest_customer
            
            unrouted_customers.remove(nearest_customer)
            print(f"Unrouted customers: {unrouted_customers}")
            print(f"Route: {route.customers}")
            print()

        if route.customers != []:
            routes.append(route.customers)

    if not unrouted_customers:
        return routes, COST
    else:
        return -1, -1


def is_feasible(route, customer_index, current_time, customers, Q, D, e0, l0, timecost_matrix):
    customer = customers[customer_index]
    current_demand = route.current_capacity + customer.demand

    if current_demand > Q:
        print(f"Try {customer_index}: Demand exceeded!")
        return False

    if not route.customers:
        arrival_time = max(customer.time_window[0], current_time + timecost_matrix[0][customer_index + 1])
    else:
        arrival_time = max(customer.time_window[0], current_time + timecost_matrix[route.customers[-1] + 1][customer_index + 1])
    
    if arrival_time > customer.time_window[1]: # li
        print(f"Try {customer_index}: Time > li!")
        return False
    
    if arrival_time + customer.service_time > l0:
        print(f"Try {customer_index}: Time > l0!")
        return False
    
    if arrival_time + customer.service_time > (D + e0):
        print(f"Try {customer_index}: Duration exceeded!")
        return False
    
    return True