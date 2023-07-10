import requests
import datetime
import time
import json
import matplotlib.pyplot as plt
import numpy as np

def get_top_n_blockchains_by_tvl(top_n=10):
    """Retrieves the top n blockchains by Total Value Locked
    Parameters
    ----------
    top_n : int, default 10
        The number of blockchains to retrieve.
    
    Returns
    -------
    top_n_blockchains : dict
        A dictionary of the top 10 blockchains and their Total Value Locked, in descending order.
    """
    # Query API to retrieve Chains and TVL
    url = "https://api.llama.fi/v2/chains"
    response = requests.get(url)
    data = response.json()

    # Convert data to dictionary for manipulation
    chain_dict = {}
    for line in data:
        chain_dict[line["name"]] = line["tvl"]
    
    # Sort dictionary by TVL by converting it into list
    sorted_chain_list = sorted(chain_dict.items(), key=lambda x: x[1], reverse=True)

    # Slice list, then convert back to dictionary
    top_n_blockchains = dict(sorted_chain_list[:top_n])

    return top_n_blockchains


def tvl_change(chain_list, from_date, to_date):
    """Retrieves the change in TVL for a list of blockchains over a specified time period.
    Parameters
    ----------
    chain_list : list
        A list of blockchain names.
    from_date : str
        A date in the format DD-MM-YYYY.
    to_date : str
        A date in the format DD-MM-YYYY.

    Returns
    -------
        A list of the top 10 blockchains by TVL, in descending order.
    """
    # Convert dates to unix time
    from_unix_time = date_to_unix_time(from_date)
    to_unix_time = date_to_unix_time(to_date)

    for chain in chain_list:
        # Query API to retrieve Chains and TVL
        url = "https://api.llama.fi/v2/historicalChainTvl/" + chain
        response = requests.get(url)
        data = response.json()

        # Write json output to respective files
        with open(f"{chain}.json", "w") as fout:
            json.dump(data, fout)
            time.sleep(3)

    change_dict = {}
    for chain in chain_list:
        # Read json output from respective files
        with open(f"{chain}.json", "r") as fin:
            data = json.load(fin)

            # Convert data to dictionary for manipulation
            chain_dict = {}
            for line in data:
                chain_dict[line["date"]] = line["tvl"]

            # Calculate TVL change
            if to_unix_time in chain_dict: 
                if from_unix_time in chain_dict:
                    tvl_change = chain_dict[to_unix_time] - chain_dict[from_unix_time]
                    print(f"{chain} TVL change: {tvl_change}")
                    change_dict[chain] = tvl_change
                else:  
                    # Dictionary starts after from_unix_time
                    earliest_date = min(chain_dict.keys())  
                    tvl_change = chain_dict[to_unix_time] - chain_dict[earliest_date]
                    print(f"{chain} TVL change from {unix_time_to_date(earliest_date)}: {tvl_change}") 
                    change_dict[chain] = tvl_change  
            else:
                print("Defined date range is not available for this chain.")

    return change_dict

def top_n_protocols_for_chain(chain, top_n=10):
    """Retrieves the top n protocols for a specified chain.
    Parameters
    ----------
    chain : str
        A blockchain name, e.g. "Arbitrum". The full list of supported chains can be found at https://defillama.com/chains.
    top_n : int, default 10
        The number of protocols to retrieve.
    
    Returns
    -------
    top_n_protocols : dict
        A dictionary of the top 10 protocols and their Total Value Locked, in descending order.
    """
    # Query API to retrieve Protocols and TVL
    url = "https://api.llama.fi/protocols/"
    response = requests.get(url)
    data = response.json()

    if data == []:
        print("No data available for this chain.")
        return

    # Convert data to dictionary for manipulation
    protocol_dict = {}
    for protocol in data:
        if chain in protocol["chainTvls"] and protocol["category"] != "CEX":
            protocol_dict[protocol["name"]] = protocol["chainTvls"]["Arbitrum"]
    
    # Sort dictionary by TVL by converting it into list
    sorted_protocol_list = sorted(protocol_dict.items(), key=lambda x: x[1], reverse=True)

    # Slice list, then convert back to dictionary
    top_n_protocols = dict(sorted_protocol_list[:top_n])

    return top_n_protocols, chain

def calculate_annualized_fee_data(protocol_list, chain="Arbitrum"):
    """Calculates the annualized fee data for a list of protocols.
    Parameters
    ----------
    protocol_list : list
        A list of protocol names.
    
    Returns
    -------
    annualized_fee_data : dict
        A dictionary of the annualized fee data for the protocols.
    """

    protocol_dict = {}

    for protocol in protocol_list:
        if "V2" in protocol or "V3" in protocol:
            API_protocol = protocol[:-3]
        elif " " in protocol:
            API_protocol = protocol.replace(" ", "-")
        else:
            API_protocol = protocol

        # Query API to retrieve Protocol Fees
        url = f"https://api.llama.fi/summary/fees/{API_protocol}?dataType=dailyFees"
        response = requests.get(url)
        data = response.json()

        if protocol == "Curve DEX":
            inner_API_protocol = "curve"
        elif protocol == "GMX":
            inner_API_protocol = "gmx"
        elif protocol == "Stargate" or protocol == "Synapse" or protocol == "Pendle":
            inner_API_protocol = protocol.lower()
        else:
            inner_API_protocol = protocol
        

        # Write json output to respective files
        with open(f"{protocol}.json", "w") as fout:
            json.dump(data, fout)
            time.sleep(2)

        # Read json output from respective files
        with open(f"{protocol}.json", "r") as fin:
            data = json.load(fin)

        if "totalDataChart" not in data:
            continue
        else:
            sum=0
            count=0
            for _, fee in data["totalDataChartBreakdown"]:
                if "arbitrum" in fee:
                    fee = fee["arbitrum"][inner_API_protocol]
                    sum+=fee
                    count+=1
            if sum == 0:
                print(f"{protocol} has no fees on {chain}")
            else:
                protocol_dict[protocol] = sum/count*365
            
    return protocol_dict



def unix_time_to_date(unix_time):
    """Converts a unix timestamp to a date.
    Parameters
    ----------
    unix_time : int
        A unix timestamp.

    Returns
    -------
    date : str
        A date in the format DD-MM-YYYY-MM.
    """
    date = datetime.datetime.fromtimestamp(unix_time).strftime("%d-%m-%Y")
    return date

def date_to_unix_time(date):
    """Converts a date to a unix timestamp.
    Parameters
    ----------
    date : str
        A date in the format DD-MM-YYYY-MM.

    Returns
    -------
    unix_time : int
        A unix timestamp.
    """
    unix_time = datetime.datetime.strptime(date, "%d-%m-%Y").replace(hour=0, minute=0, second=0).replace(tzinfo=datetime.timezone.utc).timestamp()
    return int(unix_time)

def num_to_dollars(n):
    """Converts a number to a dollar value.
    Parameters
    ----------
    n : int
        A number.

    Returns
    -------
    dollar_value : str
        A dollar value in the format $X.XX M/B/K.
    """
        
    if n > 1_000_000_000 or n < -1_000_000_000:
        return f"${n / 1_000_000_000:,.2f}B"
    if n > 1_000_000 or n < -1_000_000:
        return f"${n / 1_000_000:,.2f}M"
    if n > 1_000 or n < -1_000:
        return f"${n / 1_000:,.2f}K"
    return f"${n:,.2f}"

if __name__ == "__main__":
    '''
    EDIT THIS SECTION TO CHANGE PARAMETERS
    '''
    top_10_blockchains = get_top_n_blockchains_by_tvl()
    chain_list = list(top_10_blockchains.keys())
    tvl_list = list(top_10_blockchains.values())

    change_in_tvl = tvl_change(chain_list, "01-01-2023", "30-06-2023")

    top_10_Arbitrum_protocols, chain = top_n_protocols_for_chain("Arbitrum", 10)
    protocol_list = list(top_10_Arbitrum_protocols.keys())
    protocol_tvl_list = list(top_10_Arbitrum_protocols.values())

    annualized_fee_data = calculate_annualized_fee_data(protocol_list, chain)

    print(top_10_Arbitrum_protocols)
    print(annualized_fee_data)
    '''
    EDIT THIS SECTION TO CHANGE PARAMETERS
    '''

    figure_1 = plt.figure()
    plt.bar(chain_list, tvl_list)
    for x, y in zip(chain_list, tvl_list):
        label = num_to_dollars(y)
        plt.annotate(label,
                    (x,y),
                    textcoords="offset points",
                    xytext=(0,10),
                    ha='center')  


    plt.xlabel("Chain")
    plt.ylabel("TVL (in billions of USD)")  
    plt.title("TVL by Chain")
    plt.xticks(rotation=90)

    figure_2 = plt.figure()
    chain_list = list(change_in_tvl.keys())
    tvl_change_list = list(change_in_tvl.values())
    plt.bar(chain_list, tvl_change_list)

    for x, y in zip(chain_list, tvl_change_list):
        label = num_to_dollars(y)
        plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points", 
                    xytext=(0,5),
                    ha='center')      

    plt.xlabel("Chain")
    plt.ylabel("Change in TVL (in millions of USD)")
    plt.title("Change in TVL by Chain")
    plt.xticks(rotation=90)

    
    figure_3 = plt.figure()
    plt.bar(protocol_list, protocol_tvl_list)

    for x, y in zip(protocol_list, protocol_tvl_list):
        label = num_to_dollars(y)
        plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points", 
                    xytext=(0,5),
                    ha='center')      

    plt.xlabel("Protocol")
    plt.ylabel("TVL (in millions of USD)")
    plt.title("TVL by Protocol")
    plt.xticks(rotation=90)


    figure_4 = plt.figure()
    fee_protocol_list = list(annualized_fee_data.keys())
    annualized_fee_list = list(annualized_fee_data.values())
    plt.bar(fee_protocol_list, annualized_fee_list)

    for x, y in zip(fee_protocol_list, annualized_fee_list):
        label = num_to_dollars(y)
        plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points", 
                    xytext=(0,5),
                    ha='center')      

    plt.xlabel("Protocol")
    plt.ylabel("Annualized Fees (in millions of USD)")
    plt.title("Annualized Fees by Protocol")
    plt.xticks(rotation=90)


    figure_5, axes = plt.subplots(1,2)

    axes[0].bar(chain_list, tvl_list)
    axes[0].set_xlabel("Chain")
    axes[0].set_ylabel("TVL (in billions of USD)")
    axes[0].set_title("TVL by Chain")
    axes[0].tick_params(axis='x', labelrotation=90)

    axes[1].bar(chain_list, tvl_change_list)    
    axes[1].set_xlabel("Chain")
    axes[1].set_ylabel("Change in TVL (in millions of USD)")  
    axes[1].set_title("Change in TVL by Chain")
    axes[1].tick_params(axis='x', labelrotation=90)


    figure_6, axes1 = plt.subplots(1,2)

    axes1[0].bar(protocol_list, protocol_tvl_list) 
    axes1[0].set_xlabel("Protocol")
    axes1[0].set_ylabel("TVL (in millions of USD)")
    axes1[0].set_title("TVL by Protocol")
    axes1[0].tick_params(axis='x', labelrotation=90)


    axes1[1].bar(fee_protocol_list, annualized_fee_list)
    axes1[1].set_xlabel("Protocol")   
    axes1[1].set_ylabel("Annualized Fees (in millions of USD)") 
    axes1[1].set_title("Annualized Fees by Protocol")
    axes1[1].tick_params(axis='x', labelrotation=90)

    plt.show()