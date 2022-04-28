from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import csv

with open("contracts/crowdfund_abi.json") as file:
    abi = json.load(file)
with open("contracts/bytecode.txt") as file:
    bytecode = json.load(file)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337

address = "0x0D9bb29EeF36200bbeA73691f6E37b11f1b76396"
private_key = "793d42fa715b3fec9e8cb0f06536318c6b937c7c7ecf6f9ab0d949e49b7b987a"

# Create the contract in Python
new_contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the number of latest transaction
st.title("Create a contract")
organization_name = st.text_input("Enter your organization's name")
goal_amount = int(st.number_input("Select your fundraising goal"))
contribution_minimum = int(st.number_input("Select the minimum amount to contribute"))
beneficiary_address = st.text_input("Paste your beneficiary address")
uri = st.text_input("Paste your URI")
end_date = st.date_input("Enter your end date")
if st.button("Deploy Contract"):
    nonce = w3.eth.getTransactionCount(address)
    # build transaction
    transaction = new_contract.constructor(
        goal_amount, contribution_minimum, beneficiary_address, uri
    ).buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(
        transaction, private_key=private_key
    )
    st.write("Deploying Contract!")
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    st.write("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    st.write(f"Done! Contract deployed to {transaction_receipt.contractAddress}")
    with open("example_database.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                transaction_receipt.contractAddress,
                beneficiary_address,
                organization_name,
                goal_amount,
                contribution_minimum,
                uri,
                end_date,
            ]
        )
        file.close()
