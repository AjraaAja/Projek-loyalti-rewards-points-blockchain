
import streamlit as st
import streamlit.components.v2 as components
import json
from pathlib import Path
from web3 import Web3

# ==========================================
# KONFIGURASI
# ==========================================

st.set_page_config(
    page_title="Loyalty Reward System",
    page_icon="☕",
    layout="wide"
)

RPC_URL = "http://127.0.0.1:8545"
PROJECT_DIR = Path(__file__).parent
DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"

# ==========================================
# DESAIN UI
# ==========================================

st.markdown("""
<style>
.stApp {
    background: #0B1120;
    color: #E2E8F0;
}

section[data-testid="stSidebar"] {
    background: #111C32;
}

.block-container {
    padding-top: 2rem;
    max-width: 1150px;
}

div[data-testid="stMetric"] {
    background: #16243D;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263B5C;
}

.stButton button {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
}

.stButton button:hover {
    background: #1D4ED8;
    color: white;
}

div[data-testid="stForm"] {
    background: #111C32;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263B5C;
}

h1, h2, h3 {
    color: #F1F5F9;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# KONEKSI METAMASK
# ==========================================

WALLET_HTML = """
<div>
<button id="connect">Connect MetaMask</button>
<p id="status">Wallet belum terhubung.</p>
</div>
"""

WALLET_CSS = """
button {
    background: #2563EB;
    color: white;
    border: 0;
    padding: 10px 18px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}
p {
    color: #94A3B8;
    overflow-wrap: anywhere;
}
"""

WALLET_JS = """
export default function(component) {
    const {parentElement, setStateValue} = component;
    const button = parentElement.querySelector("#connect");
    const status = parentElement.querySelector("#status");

    let mounted = true;

    async function connect() {
        if (!window.ethereum) {
            status.textContent = "MetaMask tidak ditemukan.";
            return;
        }

        try {
            const accounts = await window.ethereum.request({
                method: "eth_requestAccounts"
            });

            const chainId = await window.ethereum.request({
                method: "eth_chainId"
            });

            if (!mounted) return;

            setStateValue("wallet", {
                address: accounts[0],
                chainId: chainId,
                connected: true
            });

            status.textContent = "Wallet terhubung: " + accounts[0];

        } catch(error) {
            status.textContent = "Koneksi gagal: " + error.message;
        }
    }

    button.addEventListener("click", connect);

    if (window.ethereum) {
        window.ethereum.on("accountsChanged", connect);
        window.ethereum.on("chainChanged", connect);
    }

    return () => {
        mounted = false;
        button.removeEventListener("click", connect);
    };
}
"""

wallet_component = components.component(
    name="loyalty_wallet",
    html=WALLET_HTML,
    css=WALLET_CSS,
    js=WALLET_JS
)

# ==========================================
# KONEKSI BLOCKCHAIN
# ==========================================

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    st.error("Hardhat RPC tidak terhubung. Jalankan npx hardhat node.")
    st.stop()

if not DEPLOYMENT_PATH.exists():
    st.error("deployment.json tidak ditemukan. Deploy kontrak dahulu.")
    st.stop()

with open(DEPLOYMENT_PATH) as f:
    deployment = json.load(f)

CONTRACT_ADDRESS = Web3.to_checksum_address(
    deployment["address"]
)

# Cari ABI secara otomatis
artifact_files = list(
    (PROJECT_DIR / "artifacts" / "contracts").rglob(
        "LoyaltyRewardToken.json"
    )
)

if not artifact_files:
    st.error("Artifact LoyaltyRewardToken tidak ditemukan. Compile kontrak dahulu.")
    st.stop()

with open(artifact_files[0]) as f:
    ABI = json.load(f)["abi"]

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)

# ==========================================
# HEADER
# ==========================================

st.title("☕ Loyalty Reward System")
st.caption("Blockchain-based Merchant & Customer Reward Platform")

col1, col2, col3 = st.columns(3)

col1.metric("Network", "Hardhat Local")
col2.metric("Chain ID", w3.eth.chain_id)
col3.metric("Latest Block", w3.eth.block_number)

st.divider()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("☕ Loyalty System")
menu = st.sidebar.radio(
    "Navigasi",
    [
        "Dashboard",
        "Customer",
        "Merchant",
        "Reward",
        "Riwayat Reward"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Merchant Blockchain Lab")

# ==========================================
# WALLET
# ==========================================

st.subheader("Wallet Connection")


wallet_result = wallet_component(
    key="loyalty_wallet_key",
    default={
        "wallet": {
            "address": "",
            "chainId": "",
            "connected": False
        }
    },
    on_wallet_change=lambda: None
)


wallet = wallet_result.wallet

address = None

if wallet and wallet.get("connected") and wallet.get("address"):
    address = Web3.to_checksum_address(wallet["address"])

    try:
        wallet_chain = int(wallet["chainId"], 16)

        if wallet_chain != w3.eth.chain_id:
            st.warning("Jaringan MetaMask berbeda dengan Hardhat RPC.")
            address = None
        else:
            st.success("Wallet berhasil terhubung.")
    except (ValueError, TypeError):
        st.error("Chain ID wallet tidak valid.")
        address = None
else:
    st.info("Hubungkan MetaMask untuk menggunakan aplikasi.")

if address:
    st.code(address)
    st.metric(
        "Saldo ETH",
        f"{float(w3.from_wei(w3.eth.get_balance(address), 'ether')):.4f} ETH"
    )

# ==========================================
# FUNGSI TRANSAKSI
# ==========================================

def send_transaction(function):
    if not address:
        st.error("Hubungkan wallet terlebih dahulu.")
        return

    try:
        tx_hash = function.transact({"from": address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            st.success("Transaksi berhasil!")
            st.code(tx_hash.hex())
        else:
            st.error("Transaksi gagal.")

    except Exception as error:
        st.error("Transaksi tidak berhasil.")
        st.caption(str(error))

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.header("Dashboard")

    st.write("Selamat datang di Loyalty Reward System.")

    if address:
        saldo = contract.functions.saldoPoinCustomer(
            address
        ).call()

        owner = contract.functions.owner().call()

        col1, col2 = st.columns(2)

        col1.metric("Saldo Loyalty Point", f"{saldo} LRT")
        col2.metric(
            "Status Akun",
            "Owner" if address.lower() == owner.lower() else "Customer"
        )

    st.divider()

    st.subheader("Informasi Smart Contract")

    st.write("Nama:", deployment["contractName"])
    st.write("Alamat Kontrak:")
    st.code(CONTRACT_ADDRESS)

# ==========================================
# CUSTOMER
# ==========================================

elif menu == "Customer":

    st.header("Customer Management")

    st.write("Daftarkan wallet sebagai customer.")

    with st.form("register_customer"):
        nama = st.text_input("Nama Customer")
        submit = st.form_submit_button("Daftar Customer")

        if submit:
            if not nama.strip():
                st.warning("Nama tidak boleh kosong.")
            else:
                send_transaction(
                    contract.functions.daftarCustomerBaru(nama)
                )

    if address:
        st.divider()
        st.subheader("Informasi Customer")

        customer = contract.functions.daftarCustomer(
            address
        ).call()

        if customer[0] != "0x0000000000000000000000000000000000000000":
            st.success(f"Terdaftar sebagai: {customer[1]}")
        else:
            st.info("Wallet ini belum terdaftar.")

        saldo = contract.functions.saldoPoinCustomer(
            address
        ).call()

        st.metric("Total Poin", f"{saldo} LRT")

# ==========================================
# MERCHANT
# ==========================================

elif menu == "Merchant":

    st.header("Merchant Management")

    merchant_ids = [
      contract.functions.getTotalMerchant(i).call()
        for i in range(contract.functions.listIdMerchantLength().call())
    ] if hasattr(contract.functions, "listIdMerchantLength") else []

    # Mengambil data merchant
    if not merchant_ids:
        st.info("Gunakan daftar merchant melalui fungsi tambahMerchant.")

    with st.expander("Tambah Merchant"):
        with st.form("add_merchant"):
            merchant_id = st.number_input(
                "ID Merchant",
                min_value=1,
                step=1
            )
            merchant_name = st.text_input("Nama Merchant")

            submit = st.form_submit_button("Tambah Merchant")

            if submit:
                if not merchant_name.strip():
                    st.warning("Nama merchant wajib diisi.")
                else:
                    send_transaction(
                        contract.functions.tambahMerchant(
                            int(merchant_id),
                            merchant_name
                        )
                    )

    st.divider()
    st.subheader("Daftar Merchant")

    total = 0

    # Getter array Solidity tidak otomatis memiliki fungsi Length.
    # Jumlah ID merchant dibaca dari storage tidak tersedia melalui ABI.
    # Masukkan ID merchant untuk memeriksa data.

    check_id = st.number_input(
        "Periksa ID Merchant",
        min_value=1,
        step=1,
        key="check_merchant"
    )

    if st.button("Cari Merchant"):
        merchant = contract.functions.daftarMerchant(
            int(check_id)
        ).call()

        if merchant[2]:
            st.success(f"Merchant: {merchant[1]}")
        else:
            st.warning("Merchant tidak ditemukan.")

# ==========================================
# REWARD
# ==========================================

elif menu == "Reward":

    st.header("Loyalty Reward")

    st.write("Berikan poin kepada customer melalui transaksi.")

    owner = contract.functions.owner().call()

    if address and address.lower() == owner.lower():

        with st.form("give_reward"):
            customer_address = st.text_input("Alamat Wallet Customer")

            merchant_id = st.number_input(
                "ID Merchant",
                min_value=1,
                step=1
            )

            transaction_id = st.text_input("ID Transaksi")

            jumlah = st.number_input(
                "Jumlah Poin",
                min_value=1,
                step=1
            )

            submit = st.form_submit_button("Berikan Reward")

            if submit:
                try:
                    customer_address = Web3.to_checksum_address(
                        customer_address
                    )

                    send_transaction(
                        contract.functions.berikanReward(
                            customer_address,
                            int(merchant_id),
                            transaction_id,
                            int(jumlah)
                        )
                    )
                except ValueError:
                    st.error("Alamat wallet tidak valid.")

    elif address:
        st.warning("Hanya owner yang dapat memberikan reward.")

    st.divider()
    st.subheader("Tukarkan Poin")

    if address:
        saldo = contract.functions.saldoPoinCustomer(address).call()

        st.metric("Saldo Poin", f"{saldo} LRT")

        with st.form("redeem_points"):
            jumlah_tukar = st.number_input(
                "Jumlah poin yang ditukar",
                min_value=1,
                step=1
            )

            submit = st.form_submit_button("Tukar Poin")

            if submit:
                if jumlah_tukar > saldo:
                    st.error("Saldo poin tidak mencukupi.")
                else:
                    send_transaction(
                        contract.functions.tukarPoin(
                            int(jumlah_tukar)
                        )
                    )

# ==========================================
# RIWAYAT REWARD
# ==========================================

elif menu == "Riwayat Reward":

    st.header("Riwayat Reward")

    st.write("Masukkan Token ID untuk melihat detail reward.")

    token_id = st.number_input(
        "Token ID",
        min_value=1,
        step=1
    )

    if st.button("Lihat Detail Reward"):

        try:
            reward = contract.functions.getReward(
                int(token_id)
            ).call()

            st.success("Data reward ditemukan.")

            col1, col2 = st.columns(2)

            col1.metric("Token ID", reward[0])
            col2.metric("Jumlah Poin", reward[4])

            st.write("Customer:", reward[1])
            st.write("Merchant ID:", reward[2])
            st.write("Transaction ID:", reward[3])
            st.write("Timestamp:", reward[5])

        except Exception:
            st.error("Data reward tidak ditemukan.")

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Loyalty Reward System | Powered by Solidity, Hardhat & Web3.py"
)
