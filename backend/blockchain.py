"""
PlasmaGrid — Blockchain Audit Trail
Network: Ethereum Sepolia Testnet
Purpose: Immutable, tamper-proof record of every resource transfer.
"""
import os
import time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

SEPOLIA_URL      = os.getenv("SEPOLIA_URL", "https://ethereum-sepolia-rpc.publicnode.com")
PRIVATE_KEY      = os.getenv("PRIVATE_KEY", "")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

w3 = Web3(Web3.HTTPProvider(SEPOLIA_URL))

# Derive wallet address from private key
try:
    WALLET = w3.eth.account.from_key(PRIVATE_KEY).address if PRIVATE_KEY else ""
except Exception:
    WALLET = ""

CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string",  "name": "fromNode", "type": "string"},
            {"internalType": "string",  "name": "toNode",   "type": "string"},
            {"internalType": "string",  "name": "resource", "type": "string"},
            {"internalType": "uint256", "name": "amount",   "type": "uint256"},
            {"internalType": "string",  "name": "reason",   "type": "string"},
        ],
        "name": "logTransfer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "index", "type": "uint256"}],
        "name": "getTransfer",
        "outputs": [
            {"internalType": "string",  "name": "", "type": "string"},
            {"internalType": "string",  "name": "", "type": "string"},
            {"internalType": "string",  "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "string",  "name": "", "type": "string"},
            {"internalType": "uint256", "name": "", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


def _get_contract():
    if not CONTRACT_ADDRESS:
        return None
    try:
        return w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI,
        )
    except Exception as e:
        print(f"[Blockchain] Contract error: {e}")
        return None


def log_transfer_on_chain(from_node: str, to_node: str, resource: str, amount: int, reason: str):
    """
    Writes one resource transfer to Ethereum Sepolia blockchain.
    Returns transaction hash string, or None if failed.
    Uses 'pending' nonce to prevent replacement transaction errors.
    """
    if not all([w3.is_connected(), WALLET, CONTRACT_ADDRESS, PRIVATE_KEY]):
        print("[Blockchain] Skipping — not configured")
        return None

    contract = _get_contract()
    if not contract:
        return None

    try:
        # Use 'pending' nonce to handle rapid successive transactions
        nonce = w3.eth.get_transaction_count(WALLET, "pending")

        txn = contract.functions.logTransfer(
            str(from_node), str(to_node),
            str(resource), int(amount), str(reason)
        ).build_transaction({
            "from":     WALLET,
            "nonce":    nonce,
            "gas":      250000,
            "gasPrice": w3.eth.gas_price,
        })

        signed  = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hex  = tx_hash.hex()

        print(f"[Blockchain] ✅ TX: {tx_hex}")

        # Small delay between transactions to avoid nonce collisions
        time.sleep(1.5)

        return tx_hex

    except Exception as e:
        print(f"[Blockchain] ❌ Failed: {e}")
        return None


def get_total_transfers() -> int:
    """Returns total number of transfers recorded on chain."""
    if not w3.is_connected() or not CONTRACT_ADDRESS:
        return 0
    try:
        contract = _get_contract()
        return contract.functions.getCount().call() if contract else 0
    except Exception:
        return 0


# ── Self-test ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\nPlasmaGrid Blockchain — Sepolia Testnet Test")
    print("=" * 45)
    print(f"Connected  : {w3.is_connected()}")
    print(f"Wallet     : {WALLET or 'NOT SET'}")
    print(f"Contract   : {CONTRACT_ADDRESS or 'NOT SET'}")
    print(f"On-chain   : {get_total_transfers()} transfers")

    if w3.is_connected() and WALLET and CONTRACT_ADDRESS:
        print("\nLogging test transfer...")
        tx = log_transfer_on_chain(
            "Manipal Hospital Bengaluru",
            "Jayadeva Institute of Cardiology",
            "blood_units", 20,
            "Critical cardiac emergency — scarcity 85/100"
        )
        if tx:
            print(f"\n✅ SUCCESS")
            print(f"TX Hash   : {tx}")
            print(f"Etherscan : https://sepolia.etherscan.io/tx/{tx}")
        else:
            print("❌ Transaction failed")
    else:
        print("\n⚠ Missing configuration — check .env file")