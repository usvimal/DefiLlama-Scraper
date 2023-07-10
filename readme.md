    DefiLlama Scraper

This project queries the Llama.fi API to retrieve data on the Total Value Locked (TVL) for various blockchains and DeFi protocols. It then plots graphs to visualize the TVL and fee distribution.

| Function                       | Description                                                                   |
|--------------------------------|-------------------------------------------------------------------------------|
| get_top_n_blockchains_by_tvl() | Retrieves the top n blockchains by TVL                                        |
| tvl_change()                   | Calculates the change in TVL for a list of blockchains over a period of time  |
| top_n_protocols_for_chain()    | Retrieves the top n protocols by TVL for a specified chain                    |
| calculate_annualized_fee_data()| Calculates the annualized fee data for a list of protocols                    |


Example Usage
```
python

top_10_blockchains = get_top_n_blockchains_by_tvl(top_n=10)

chain_list = tvl_change(chain_list, "01-01-2023", "30-06-2023")

top_10_Arbitrum_protocols, chain = top_n_protocols_for_chain("Arbitrum", 10)

annualized_fee_data = calculate_annualized_fee_data(protocol_list, chain)
```

Visualizations

The script generates several matplotlib plots:

    TVL by chain
    Change in TVL by chain
    TVL by protocol
    Annualized fees by protocol

Requirements

    requests
    matplotlib
    numpy
