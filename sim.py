
""" Defining the Parametres  via user input """

# gold_volume=float(input("Total number of gold in the system in gm:  "))

# buy_start=float(input("Min gm to buy gold:  "))
# buy_end=float(input("Max  gm to buy gold:  "))

# buy_transaction_range=(buy_start,buy_end)

# sell_start=float(input("Min gm to sell gold :  "))
# sell_end=float(input("Max gm to sell gold:  "))

# sell_transaction_range=(sell_start,sell_end)


gold_volume = 10000  # in gm 
buy_start = 0.001  # Minimum buy limit in gm
buy_end = 9.99  # Maximum buy limit in gm 

buy_transaction_range = (buy_start, buy_end)

sell_start = 0.001
sell_end = 9.99

sell_transaction_range = (sell_start, sell_end)


""" Creating a Rack Object """



class Rack:
    def __init__(self, capacity, quantity):
        self.capacity = float(capacity)
        self.quantity = float(quantity)

    def is_full(self):
        return self.quantity >= self.capacity  # True if full or else it will be false

    def remaining_capacity(self):
        return self.capacity - self.quantity

    def __repr__(self):
        return f"Rack(Capacity: {self.capacity}, Quantity: {round(self.quantity, 3)}, Full: {self.is_full()})"


""" Dfining ware house """


warehouse = Rack(10000, 5000)


"""Creatng the configuration for the Rack """

in_config = {
    "num": 5,
    "racks": [
        Rack(10.0, 5.0),
        Rack(20.0, 10.0),
        Rack(30.0, 15.0),
        Rack(50.0, 25.0),
        Rack(10.0, 5.0)
    ]
}


# for i in range(num_in_racks):
#     while True:
#         capacity = float(input(f"Enter the capacity of IN Rack number {i+1}: "))
#         quantity = float(input(f"Enter the current Volume of IN Rack number {i+1}: "))

#         if capacity > quantity:
#             in_config["racks"].append(Rack(capacity, quantity))
#             break
#         else:
#             print("Error: Capacity must be alwsy greater that the current . Please re-enter values.")



# num_out_racks=int(input("Enter the Total number of Out racks: "))


out_config = {
    "num": 5,
    "racks": [
        Rack(10.0, 4.0),
        Rack(20.0, 12.0),
        Rack(30.0, 8.0),
        Rack(50.0, 40.0),
        Rack(10.0, 6.0)
    ]
}


# for i in range(num_out_racks):
#     while True:
#         capacity = float(input(f"Enter the capacity of OUT Rack number {i+1}: "))
#         quantity = float(input(f"Enter the current Volume of OUT Rack number {i+1}: "))

#         if capacity > quantity:
#             out_config["racks"].append(Rack(capacity, quantity))
#             break
#         else:
#             print("Error: Capacity must be alwsy greater that the current . Please re-enter values.")



"""  Rack selection Algorithm MIN  and MAX capacity remaining"""


""" Rack Selection Algorithm (Source & Destination) """

def source_rack_selection(list_of_racks, required_gold):
    """ 
    Should select the rack with least remianing capacity 
    but should also prefer rack with suffient gold
    """
    selected_rack = None

    for rack in list_of_racks:
        remaining_capacity = rack.capacity - rack.quantity

        #prefer rack with sufient gold 
        if rack.quantity >= required_gold:
            if selected_rack is None or selected_rack.quantity < required_gold or remaining_capacity < (selected_rack.capacity - selected_rack.quantity):
                selected_rack = rack
        else:
            # use rebalancing
            if selected_rack is None or (selected_rack.quantity < required_gold and selected_rack.capacity - selected_rack.quantity > remaining_capacity):
                selected_rack = rack

    return selected_rack

def destination_rack_selection(list_of_racks):
    """ Selects the rack with the most remaining capacity (most available space) """
    selected_rack = None
    for rack in list_of_racks:
        remaining_capacity = rack.capacity - rack.quantity
        if selected_rack is None or (selected_rack.capacity - selected_rack.quantity < remaining_capacity):
            selected_rack = rack
    return selected_rack


""" Out Rack Rebalancing """

def rack_balancing_out(out_rack, warehouse, req_gold):
    """ 
    Ensures the out rack has enough gold to fulfill a transaction.
    Transfers gold from the warehouse if needed.
    """
    if out_rack.quantity >= req_gold:
        return True  

    shortfall = req_gold - out_rack.quantity

    if warehouse.quantity >= shortfall:
        out_rack.quantity += shortfall
        warehouse.quantity -= shortfall
        return True  

    print("Transaction failed: Not enough gold in the warehouse.")
    return False  


""" In Rack Rebalancing """
def rack_balancing_in(in_rack, in_racks, required_gold):
    """ 
    Transfers gold from other IN racks if the selected rack lacks enough for a transaction.
    Ensures rebalancing from multiple racks if needed.
    """
    if in_rack.quantity >= required_gold:
        return True  # No need for rebalancing

    shortfall = required_gold - in_rack.quantity
    donor_candidates = sorted(

        [rack for rack in in_racks if rack != in_rack and rack.quantity > 0],
        key=lambda rack: rack.quantity,
        reverse=True
    )  # Sort donors by quantity (highest first)

    if not donor_candidates:
        print("Transaction failed: No available IN racks for rebalancing.")
        return False

    # Distribute shortfall acros multiple inrack
    for donor_rack in donor_candidates:
        transfer_amount = min(donor_rack.quantity, shortfall)
        in_rack.quantity += transfer_amount
        donor_rack.quantity -= transfer_amount
        shortfall -= transfer_amount

        if shortfall == 0:  # check is that rebalancde 
            return True  

    print("Transaction failed: No enough gold after rebalancing.")
    return False 


""" Sell Transaction with Rebalancing """
def sell_transaction(in_racks, out_racks, sell_quantity):
    source_in_rack = source_rack_selection(in_racks, sell_quantity)
    destination_out_rack = destination_rack_selection(out_racks)

    if source_in_rack.quantity >= sell_quantity:
        source_in_rack.quantity -= sell_quantity
        destination_out_rack.quantity += sell_quantity
        return True  

    shortfall = sell_quantity - source_in_rack.quantity

    if rack_balancing_in(source_in_rack, in_racks, shortfall):
        if source_in_rack.quantity >= sell_quantity:
            source_in_rack.quantity -= sell_quantity
            destination_out_rack.quantity += sell_quantity
            return True  

    print("Transaction failed: Not enough gold available for selling.")
    return False


""" Buy Transaction with Rebalancing """

def buy_transaction(in_racks, out_racks, buy_quantity, warehouse):
    source_out_rack = source_rack_selection(out_racks, buy_quantity)  # Take from an OUT rack
    destination_in_rack = destination_rack_selection(in_racks)  # Move to an IN rack

    if source_out_rack.quantity >= buy_quantity:
        source_out_rack.quantity -= buy_quantity
        destination_in_rack.quantity += buy_quantity
        return True  

    shortfall = buy_quantity - source_out_rack.quantity

    if rack_balancing_out(source_out_rack, warehouse, shortfall):
        source_out_rack.quantity -= buy_quantity
        destination_in_rack.quantity += buy_quantity
        return True  

    print("Transaction failed: Not enough gold available for buying.")
    return False



""" Testing of code """
import random

def print_rack_status(in_racks, out_racks, warehouse):
    print("\n=== Current Rack Status ===")
    print(f"Warehouse: {warehouse} | Remaining Capacity: {warehouse.remaining_capacity():.3f} gm")
    
    print("IN Racks:")
    for i, rack in enumerate(in_racks):
        print(f"  IN Rack {i+1}: {rack} | Remaining Capacity: {rack.remaining_capacity():.3f} gm")
    
    print("OUT Racks:")
    for i, rack in enumerate(out_racks):
        print(f"  OUT Rack {i+1}: {rack} | Remaining Capacity: {rack.remaining_capacity():.3f} gm")
    
    print("===========================\n")


def test_transactions(in_racks, out_racks, warehouse, buy_range, sell_range):
    print("Starting Simulation...\n")
    print_rack_status(in_racks, out_racks, warehouse)


    buy_qty = round(random.uniform(*buy_range), 3)
    print(f"Buying {buy_qty} gm of gold...")
    buy_transaction(in_racks, out_racks, buy_qty, warehouse)
    print_rack_status(in_racks, out_racks, warehouse)

  
    sell_qty = round(random.uniform(*sell_range), 3)
    print(f"Selling {sell_qty} gm of gold...")
    sell_transaction(in_racks, out_racks, sell_qty)
    print_rack_status(in_racks, out_racks, warehouse)

   
    sell_qty = round(random.uniform(*sell_range), 3)
    print(f"Selling {sell_qty} gm of gold...")
    sell_transaction(in_racks, out_racks, sell_qty)
    print_rack_status(in_racks, out_racks, warehouse)

    print("Simulation Complete!\n")

# Run the test
test_transactions(in_config["racks"], out_config["racks"], warehouse, buy_transaction_range, sell_transaction_range)






