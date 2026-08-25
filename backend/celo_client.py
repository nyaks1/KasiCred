import os
import json
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("CELO_RPC_URL", "https://forno.celo-sepolia.celo-testnet.org")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("RELAYER_PRIVATE_KEY")

ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "address", "name": "vendor", "type": "address"},
            {"internalType": "bytes32", "name": "reviewHash", "type": "bytes32"},
            {"internalType": "uint8", "name": "score", "type": "uint8"}
        ],
        "name": "recordReview",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "vendor", "type": "address"}
        ],
        "name": "getVendorSummary",
        "outputs": [
            {"internalType": "uint256", "name": "averageScore", "type": "uint256"},
            {"internalType": "uint256", "name": "count", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

def get_contract():
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS environment variable is not set.")
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

def verify_connection():
    return {
        "connected": w3.is_connected(),
        "block_number": w3.eth.block_number,
        "chain_id": w3.eth.chain_id,
        "contract_address": CONTRACT_ADDRESS
    }

def get_vendor_summary(vendor_address: str):
    contract = get_contract()
    checksum = Web3.to_checksum_address(vendor_address)
    avg_score, count = contract.functions.getVendorSummary(checksum).call()
    return {"average_score": avg_score, "review_count": count}

def record_review_onchain(vendor_address: str, review_hash: bytes, score: int) -> str:
    if not PRIVATE_KEY:
        raise ValueError("RELAYER_PRIVATE_KEY is required to submit transactions.")
    
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = get_contract()
    
    tx = contract.functions.recordReview(
        Web3.to_checksum_address(vendor_address),
        review_hash,
        score
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.to_hex(tx_hash)