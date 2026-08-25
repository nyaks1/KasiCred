import os
import json
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# Network RPC Configuration (Celo Sepolia Testnet)
RPC_URL = os.getenv("CELO_RPC_URL", "https://forno.celo-sepolia.celo-testnet.org")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Relayer private key for gasless backend transaction signing
PRIVATE_KEY = os.getenv("RELAYER_PRIVATE_KEY")

# Target deployed contract address
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Complete ABI matching KasiCredTrustLedger.sol
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
    """Instantiates and returns the smart contract instance."""
    if not CONTRACT_ADDRESS:
        raise ValueError("CONTRACT_ADDRESS is not defined in the environment variables.")
    return w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

def verify_connection() -> dict:
    """Verifies node connectivity, active chain ID, and current block height."""
    return {
        "connected": w3.is_connected(),
        "block_number": w3.eth.block_number if w3.is_connected() else None,
        "chain_id": w3.eth.chain_id if w3.is_connected() else None,
        "rpc_url": RPC_URL,
        "contract_address": CONTRACT_ADDRESS
    }

def get_vendor_summary(vendor_address: str) -> dict:
    """Performs a free read call against the deployed ledger contract."""
    contract = get_contract()
    checksum_vendor = Web3.to_checksum_address(vendor_address)
    avg_score, count = contract.functions.getVendorSummary(checksum_vendor).call()
    return {
        "average_score": avg_score,
        "review_count": count
    }

def record_review_onchain(vendor_address: str, review_hash: bytes, score: int) -> str:
    """
    Constructs, signs, and broadcasts a transaction to the Celo Sepolia network
    using the relayer account.
    """
    if not PRIVATE_KEY:
        raise ValueError("RELAYER_PRIVATE_KEY is required to sign transactions.")

    # Instantiate relayer account
    relayer_account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = get_contract()
    checksum_vendor = Web3.to_checksum_address(vendor_address)

    # Fetch fresh transaction nonce and gas parameters
    nonce = w3.eth.get_transaction_count(relayer_account.address)
    gas_price = w3.eth.gas_price

    # Build the contract transaction
    transaction = contract.functions.recordReview(
        checksum_vendor,
        review_hash,
        score
    ).build_transaction({
        'from': relayer_account.address,
        'nonce': nonce,
        'gasPrice': gas_price,
        'chainId': w3.eth.chain_id
    })

    # Estimate gas limit
    try:
        transaction['gas'] = w3.eth.estimate_gas(transaction)
    except Exception:
        transaction['gas'] = 150000

    # Sign raw transaction
    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    return w3.to_hex(tx_hash)

if __name__ == "__main__":
    print("Testing Celo Testnet Connectivity...")
    status = verify_connection()
    print(f"Connection Status: {status}")