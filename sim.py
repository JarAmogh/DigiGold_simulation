
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
    Selects the best source rack for both buying (out racks) and selling (in racks).
    
    1. Finds racks with at the required_gold.
    2. Selects the rack with the minimum remaining capacity.
    """
    selected_rack = None
    min_remaining_capacity = float('inf')

    for rack in list_of_racks:
        remaining_capacity = rack.capacity - rack.quantity

        if rack.quantity >= required_gold:  
            if remaining_capacity < min_remaining_capacity:
                selected_rack = rack
                min_remaining_capacity = remaining_capacity

    return selected_rack  





def destination_rack_selection(list_of_racks, required_gold):
    """
    Selects the best destination rack for both buying (in racks) and selling (out racks).
    
    1. Finds racks with enough free space for requried gold 
    2. Selects the rack with the minimum remaining capacity.
    """
    selected_rack = None
    min_remaining_capacity = float('inf')

    for rack in list_of_racks:
        remaining_capacity = rack.capacity - rack.quantity

        if remaining_capacity >= required_gold:
            if remaining_capacity < min_remaining_capacity:
                selected_rack = rack
                min_remaining_capacity = remaining_capacity

    return selected_rack  



""" Out Rack Rebalancing """
def rebalance_out_racks(out_racks, warehouse):
    """
    Rebalances OUT racks by taking gold from the warehouse only.
    """

    if warehouse.quantity <= 0:
        print(" Warehouse has no sufficient amout of gold .")
        return

    
    for i in range(len(out_racks) - 1):
        for j in range(i + 1, len(out_racks)):
            if out_racks[i].remaining_capacity() > out_racks[j].remaining_capacity():
                out_racks[i], out_racks[j] = out_racks[j], out_racks[i]

    for rack in out_racks:
        if warehouse.quantity <= 0:
            break

        remaining_capacity = rack.remaining_capacity()
        if remaining_capacity > 0:
            gold_to_transfer = min(remaining_capacity, warehouse.quantity)
            rack.quantity += gold_to_transfer
            warehouse.quantity -= gold_to_transfer
            print(f"Moved {gold_to_transfer:.3f} gm from Warehouse to {rack}")

    print("✅ Rebalancing done !\n")



""" In Rack Rebalancing """


def rebalance_in_racks(in_racks):
    """
    Rebalances IN racks by redistributing gold among themselves.
    It does NOT take gold from the warehouse.
    """

    total_gold = sum(rack.quantity for rack in in_racks) 
    total_capacity = sum(rack.capacity for rack in in_racks)  

    if total_gold == 0:
        print("No gold available in IN racks for rebalancing.")
        return

    avg_gold_per_rack = total_gold / len(in_racks)

    for rack in in_racks:
        rack.quantity = min(avg_gold_per_rack, rack.capacity)  

    print(" Rebalancing complete: Gold redistributed among IN racks.")


""" Sell Transaction with Rebalancing """
def seller_action(in_racks, out_racks, required_gold):
    """
    Handles the selling process:
    1. Selects the best source rack from IN racks.
    2. Selects the best destination rack from OUT racks.
    3. Moves gold from IN to OUT racks.
    4. If insufficient gold, rebalances IN racks and retries.
    """
    source_rack = source_rack_selection(in_racks, required_gold)

    if not source_rack:
        print("Insufficient gold in IN racks! Rebalancing...")
        rebalance_in_racks(in_racks)
        source_rack = source_rack_selection(in_racks, required_gold)

    if source_rack:
        destination_rack = destination_rack_selection(out_racks, required_gold)

        if destination_rack:
            source_rack.quantity -= required_gold
            destination_rack.quantity += required_gold
            print(f" Sold {required_gold} gm from {source_rack} to {destination_rack}")
        else:
            print("No suitable OUT rack found for storage!")
    else:
        print("Still insufficient gold after rebalancing!")


""" Buy Transaction with Rebalancing """

def buyer_action(out_racks, in_racks, required_gold):
    """
    Handles the buying process:
    1. Selects the best source rack from OUT racks.
    2. Selects the best destination rack from IN racks.
    3. Moves gold from OUT to IN racks.
    4. If insufficient gold, rebalances OUT racks and retries.
    """
    source_rack = source_rack_selection(out_racks, required_gold)

    if not source_rack:
        print("Insufficient gold in OUT racks! Rebalancing...")
        rebalance_out_racks(out_racks)
        source_rack = source_rack_selection(out_racks, required_gold)

    if source_rack:
        destination_rack = destination_rack_selection(in_racks, required_gold)

        if destination_rack:
            source_rack.quantity -= required_gold
            destination_rack.quantity += required_gold
            print(f" Bought {required_gold} gm from {source_rack} to {destination_rack}")
        else:
            print(" No suitable IN rack found for storage!")
    else:
        print(" Still insufficient gold after rebalancing!")



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


import random


def test_gold_transactions(in_racks, out_racks, warehouse, buy_range, sell_range):
    print("\n Staring the transaction\n")

    print_rack_status(in_racks, out_racks, warehouse)


    buy_qty = round(random.uniform(*buy_range), 3)
    print(f"\n Attempting to BUY {buy_qty} gm of gold...")
    buyer_action(out_racks, in_racks, buy_qty)
    print_rack_status(in_racks, out_racks, warehouse)


    sell_qty = round(random.uniform(*sell_range), 3)
    print(f"\n Attempting to SELL {sell_qty} gm of gold...")
    seller_action(in_racks, out_racks, sell_qty)
    print_rack_status(in_racks, out_racks, warehouse)

   
    sell_qty = round(random.uniform(*sell_range), 3)
    print(f"\n Attempting to SELL {sell_qty} gm of gold...")
    seller_action(in_racks, out_racks, sell_qty)
    print_rack_status(in_racks, out_racks, warehouse)

    print("End")

# Run the test
test_gold_transactions(in_config["racks"], out_config["racks"], warehouse, buy_transaction_range, sell_transaction_range)
