import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v2 as components
from web3 import Web3

# ==========================================
# KONFIGURASI
# ==========================================
st.set_page_config(page_title="Loyalty Reward System", page_icon="☕", layout="wide")

RPC_URL = "http://127.0.0.1:8545"
PROJECT_DIR = Path(__file__).parent
DEPLOYMENT_PATH = PROJECT_DIR / "deployment.json"
MAX_PROBE = 500  # batas aman saat membaca array tanpa getter length
ZERO = "0x0000000000000000000000000000000000000000"

# Palet kalem: slate gelap + sage/teal lembut + pasir hangat
ACCENT = "#6FB3A5"

# ==========================================
# DESAIN UI
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(1200px 600px at 85% -10%, #1B2A3F 0%, rgba(27,42,63,0) 60%),
                linear-gradient(180deg, #0F1724 0%, #121C2D 100%);
    color: #E6EAF2;
}
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 1150px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #131D2E 0%, #101826 100%);
    border-right: 1px solid #223048;
}
section[data-testid="stSidebar"] h1 { font-size: 1.25rem; color: #E6EAF2; }

/* Judul */
h1, h2, h3 { color: #EEF2F8; letter-spacing: -0.01em; }
h2 { font-weight: 650; }

/* Hero */
.lr-hero {
    background: linear-gradient(135deg, #1A2B40 0%, #172338 55%, #1C2F3A 100%);
    border: 1px solid #263A55;
    border-radius: 18px;
    padding: 26px 30px;
    margin-bottom: 18px;
    display: flex; justify-content: space-between; align-items: center; gap: 20px;
    flex-wrap: wrap;
}
.lr-eyebrow { font-size: 0.72rem; letter-spacing: 0.14em; color: #8FB9B0; font-weight: 600; }
.lr-hero h1 { margin: 4px 0 4px 0; padding: 0; font-size: 1.8rem; }
.lr-hero p { margin: 0; color: #9AA8BD; font-size: 0.95rem; }

/* Chip / badge */
.chip {
    display: inline-block; padding: 5px 12px; margin: 3px 4px 3px 0;
    border-radius: 999px; font-size: 0.8rem; font-weight: 500;
    background: #1B2A40; border: 1px solid #2A3E5C; color: #C3CEDF;
}
.chip.ok { background: #1A3033; border-color: #2D5A57; color: #9AD3C6; }
.chip.warn { background: #33291C; border-color: #5F4B2B; color: #E0C48E; }
.chip.owner { background: #2A2638; border-color: #4A4270; color: #BDB2E6; }

/* Kartu */
.lr-card {
    background: #151F31; border: 1px solid #243249; border-radius: 14px;
    padding: 18px 20px; height: 100%;
}
.lr-label { font-size: 0.78rem; color: #8A9AB2; font-weight: 500; letter-spacing: 0.02em; }
.lr-value { font-size: 1.7rem; font-weight: 650; color: #EEF2F8; margin-top: 4px; }
.lr-hint { font-size: 0.78rem; color: #6F809A; margin-top: 2px; }
.lr-sub { color: #8A9AB2; margin: -6px 0 18px 0; font-size: 0.92rem; }

/* Metric bawaan */
div[data-testid="stMetric"] {
    background: #151F31; padding: 16px 18px; border-radius: 14px; border: 1px solid #243249;
}
div[data-testid="stMetricLabel"] { color: #8A9AB2; }

/* Tombol */
.stButton button, div[data-testid="stFormSubmitButton"] button {
    background: #3F8F82; color: #F5FAF9; border: none; border-radius: 10px;
    padding: 0.5rem 1.2rem; font-weight: 600; transition: all .15s ease;
}
.stButton button:hover, div[data-testid="stFormSubmitButton"] button:hover {
    background: #4BA396; color: #FFFFFF; transform: translateY(-1px);
}

/* Form & container */
div[data-testid="stForm"] {
    background: #131D2E; padding: 20px; border-radius: 14px; border: 1px solid #243249;
}
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; }

/* Input */
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div {
    background: #0F1826 !important; border-radius: 10px !important;
}
div[data-baseweb="input"] { border: 1px solid #27374F !important; }
div[data-baseweb="input"]:focus-within { border-color: #5FA89B !important; }

/* Tab */
button[data-baseweb="tab"] { color: #8A9AB2; font-weight: 500; }
button[data-baseweb="tab"][aria-selected="true"] { color: #A6D9CE; }
div[data-baseweb="tab-highlight"] { background-color: #6FB3A5 !important; }

/* Alert & tabel */
div[data-testid="stAlert"] { border-radius: 12px; }
div[data-testid="stDataFrame"] { border: 1px solid #243249; border-radius: 12px; overflow: hidden; }
hr { border-color: #223048 !important; }
code { color: #A6D9CE !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# KOMPONEN METAMASK
# ==========================================
WALLET_HTML = """
<div>
<button id="connect">Connect MetaMask</button>
<p id="status">Wallet belum terhubung.</p>
</div>
"""
WALLET_CSS = """
button { background:#3F8F82; color:#F5FAF9; border:0; padding:10px 18px;
         border-radius:10px; cursor:pointer; font-weight:600; font-family:inherit; }
button:hover { background:#4BA396; }
p { color:#8A9AB2; overflow-wrap:anywhere; font-size:0.9rem; }
"""
WALLET_JS = """
export default function(component) {
    const {parentElement, setStateValue} = component;
    const button = parentElement.querySelector("#connect");
    const status = parentElement.querySelector("#status");
    let mounted = true;

    async function connect() {
        if (!window.ethereum) { status.textContent = "MetaMask tidak ditemukan."; return; }
        try {
            const accounts = await window.ethereum.request({method: "eth_requestAccounts"});
            const chainId = await window.ethereum.request({method: "eth_chainId"});
            if (!mounted) return;
            setStateValue("wallet", {address: accounts[0], chainId: chainId, connected: true});
            status.textContent = "Wallet terhubung: " + accounts[0];
        } catch (error) {
            status.textContent = "Koneksi gagal: " + error.message;
        }
    }

    button.addEventListener("click", connect);
    if (window.ethereum) {
        window.ethereum.on("accountsChanged", connect);
        window.ethereum.on("chainChanged", connect);
    }
    return () => { mounted = false; button.removeEventListener("click", connect); };
}
"""
wallet_component = components.component(
    name="loyalty_wallet", html=WALLET_HTML, css=WALLET_CSS, js=WALLET_JS
)

# ==========================================
# KONEKSI BLOCKCHAIN
# ==========================================
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    st.error("Hardhat RPC tidak terhubung. Jalankan: npx hardhat node")
    st.stop()

if not DEPLOYMENT_PATH.exists():
    st.error("deployment.json tidak ditemukan. Deploy kontrak dahulu.")
    st.stop()

with open(DEPLOYMENT_PATH) as f:
    deployment = json.load(f)

CONTRACT_ADDRESS = Web3.to_checksum_address(deployment["address"])

artifact_files = list((PROJECT_DIR / "artifacts" / "contracts").rglob("LoyaltyRewardToken.json"))
if not artifact_files:
    st.error("Artifact LoyaltyRewardToken tidak ditemukan. Jalankan: npx hardhat compile")
    st.stop()

with open(artifact_files[0]) as f:
    ABI = json.load(f)["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Cek kesehatan: pastikan alamat di deployment.json benar-benar kontrak ini
try:
    owner_address = contract.functions.owner().call()
except Exception:
    code_size = len(w3.eth.get_code(CONTRACT_ADDRESS))
    st.error(
        "Kontrak di alamat deployment.json tidak cocok dengan ABI LoyaltyRewardToken. "
        "Biasanya karena node Hardhat di-restart atau kontrak diubah tanpa deploy ulang."
    )
    st.write("Alamat di deployment.json:")
    st.code(CONTRACT_ADDRESS)
    st.write(f"Ukuran kode di alamat itu: {code_size} byte"
             + (" (kosong, tidak ada kontrak)" if code_size == 0 else ""))
    st.write("ABI dibaca dari:")
    st.code(str(artifact_files[0]))
    st.info(
        "Perbaikan: jalankan `npx hardhat compile`, lalu "
        "`npx hardhat run scripts/deploy.js --network localhost`, "
        "kemudian refresh halaman ini."
    )
    st.stop()

# ==========================================
# HELPER TAMPILAN
# ==========================================
def short(addr):
    return f"{addr[:6]}…{addr[-4:]}" if addr else "-"


def card(label, value, hint=""):
    st.markdown(
        f'<div class="lr-card"><div class="lr-label">{label}</div>'
        f'<div class="lr-value">{value}</div><div class="lr-hint">{hint}</div></div>',
        unsafe_allow_html=True,
    )


def page_header(title, subtitle):
    st.markdown(f"## {title}")
    st.markdown(f'<div class="lr-sub">{subtitle}</div>', unsafe_allow_html=True)


# ==========================================
# FUNGSI MEMBACA DATA DARI SMART CONTRACT
# ==========================================
def get_merchants():
    total = contract.functions.getTotalMerchant().call()
    rows = []
    for i in range(total):
        mid = contract.functions.listIdMerchant(i).call()
        m = contract.functions.daftarMerchant(mid).call()
        rows.append({"ID Merchant": m[0], "Nama": m[1], "Terdaftar": m[2]})
    return rows


def get_rewards():
    """listTokenIdReward tidak punya getter length -> baca indeks sampai revert."""
    rows = []
    for i in range(MAX_PROBE):
        try:
            token_id = contract.functions.listTokenIdReward(i).call()
        except Exception:
            break
        r = contract.functions.getReward(token_id).call()
        rows.append({
            "Token ID": r[0],
            "Customer": r[1],
            "Merchant ID": r[2],
            "Transaction ID": r[3],
            "Poin (LRT)": r[4],
            "Waktu": datetime.fromtimestamp(r[5]).strftime("%Y-%m-%d %H:%M:%S"),
        })
    return rows


def get_customers(rewards):
    """Kontrak tidak punya array customer -> ambil dari penerima reward."""
    rows = []
    for addr in sorted({r["Customer"] for r in rewards}):
        c = contract.functions.daftarCustomer(addr).call()
        saldo = contract.functions.saldoPoinCustomer(addr).call()
        rows.append({"Wallet": addr, "Nama": c[1], "Saldo Poin (LRT)": saldo})
    return rows


# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("☕ Loyalty System")
menu = st.sidebar.radio(
    "Navigasi",
    ["Dashboard", "Data Management", "Form Input", "Detail Data", "Wallet & Transaction"],
)
st.sidebar.divider()
st.sidebar.caption("Merchant Blockchain Lab")

# ==========================================
# HERO
# ==========================================
st.markdown(
    '<div class="lr-hero"><div>'
    '<div class="lr-eyebrow">BLOCKCHAIN LOYALTY PLATFORM</div>'
    '<h1>☕ Loyalty Reward System</h1>'
    '<p>Kelola merchant, customer, dan reward poin yang tercatat di smart contract.</p>'
    '</div><div>'
    f'<span class="chip ok">● Hardhat Local</span>'
    f'<span class="chip">Chain {w3.eth.chain_id}</span>'
    f'<span class="chip">Block {w3.eth.block_number}</span>'
    '</div></div>',
    unsafe_allow_html=True,
)

# ==========================================
# WALLET (dipakai semua halaman)
# ==========================================
with st.container(border=True):
    wallet_result = wallet_component(
        key="loyalty_wallet_key",
        default={"wallet": {"address": "", "chainId": "", "connected": False}},
        on_wallet_change=lambda: None,
    )

wallet = wallet_result.wallet
address = None
can_sign = False
wallet_msg = ("info", "Hubungkan MetaMask untuk menggunakan aplikasi.")

if wallet and wallet.get("connected") and wallet.get("address"):
    try:
        wallet_chain = int(wallet["chainId"], 16)
        if wallet_chain != w3.eth.chain_id:
            wallet_msg = ("warning", "Jaringan MetaMask berbeda dengan Hardhat RPC (Chain ID 31337).")
        else:
            address = Web3.to_checksum_address(wallet["address"])
            can_sign = address in w3.eth.accounts
            if can_sign:
                wallet_msg = ("success", "Wallet berhasil terhubung.")
            else:
                wallet_msg = (
                    "warning",
                    "Akun ini tidak dikenali node Hardhat, jadi tidak bisa mengirim transaksi. "
                    "Gunakan akun hasil import dari daftar Accounts di terminal `npx hardhat node`.",
                )
    except (ValueError, TypeError):
        wallet_msg = ("error", "Chain ID wallet tidak valid.")

getattr(st, wallet_msg[0])(wallet_msg[1])

is_owner = bool(address) and address.lower() == owner_address.lower()
is_customer = bool(address) and contract.functions.daftarCustomer(address).call()[0] != ZERO

if address:
    role_chip = (
        '<span class="chip owner">Owner</span>' if is_owner
        else '<span class="chip ok">Customer</span>' if is_customer
        else '<span class="chip warn">Belum terdaftar</span>'
    )
    saldo_eth = float(w3.from_wei(w3.eth.get_balance(address), "ether"))
    st.markdown(
        f'<span class="chip">👛 {short(address)}</span>{role_chip}'
        f'<span class="chip">{saldo_eth:,.2f} ETH</span>',
        unsafe_allow_html=True,
    )

st.write("")

# ==========================================
# TRANSAKSI + LOG STATUS
# ==========================================
if "tx_log" not in st.session_state:
    st.session_state.tx_log = []


def log_tx(nama, status, tx_hash="-", detail=""):
    st.session_state.tx_log.insert(0, {
        "Waktu": datetime.now().strftime("%H:%M:%S"),
        "Fungsi": nama,
        "Status": status,
        "Tx Hash": tx_hash,
        "Detail": detail,
    })


def send_transaction(nama_fungsi, function):
    if not address:
        st.error("Hubungkan wallet terlebih dahulu.")
        return False
    if not can_sign:
        st.error("Akun MetaMask ini tidak dikenali node Hardhat. Import akun dari daftar Accounts Hardhat.")
        return False

    with st.status(f"Menunggu konfirmasi: {nama_fungsi} ...", expanded=True) as box:
        try:
            tx_hash = function.transact({"from": address}).hex()
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            if receipt.status == 1:
                box.update(label="Transaksi berhasil", state="complete")
                st.code(tx_hash)
                st.caption(f"Block {receipt.blockNumber} | Gas {receipt.gasUsed}")
                log_tx(nama_fungsi, "Berhasil", tx_hash)
                return True
            box.update(label="Transaksi gagal", state="error")
            log_tx(nama_fungsi, "Gagal", tx_hash)
        except Exception as error:
            box.update(label="Transaksi ditolak kontrak", state="error")
            st.caption(str(error))
            log_tx(nama_fungsi, "Gagal", "-", str(error)[:120])
    return False


# ==========================================
# 1. DASHBOARD
# ==========================================
if menu == "Dashboard":
    page_header("Dashboard", "Ringkasan kondisi jaringan dan data loyalty saat ini.")

    merchants = get_merchants()
    rewards = get_rewards()
    customers = get_customers(rewards)
    total_poin_diberikan = sum(r["Poin (LRT)"] for r in rewards)
    poin_beredar = sum(c["Saldo Poin (LRT)"] for c in customers)

    c1, c2, c3 = st.columns(3)
    with c1:
        card("Status Blockchain", "Terhubung", "Hardhat RPC aktif")
    with c2:
        card("Chain ID", w3.eth.chain_id, "Jaringan lokal")
    with c3:
        card("Latest Block", w3.eth.block_number, "Blok terbaru")

    st.write("")
    c4, c5, c6, c7 = st.columns(4)
    with c4:
        card("Total Merchant", len(merchants), "Terdaftar di kontrak")
    with c5:
        card("Total Reward", len(rewards), "NFT yang di-mint")
    with c6:
        card("Poin Diberikan", f"{total_poin_diberikan}", "LRT")
    with c7:
        card("Poin Beredar", f"{poin_beredar}", "Saldo customer (LRT)")

    if rewards:
        st.write("")
        st.subheader("Poin per Merchant")
        df = pd.DataFrame(rewards).groupby("Merchant ID", as_index=False)["Poin (LRT)"].sum()
        df["Merchant ID"] = df["Merchant ID"].astype(str)
        st.bar_chart(df, x="Merchant ID", y="Poin (LRT)", color=ACCENT, height=240)

    st.divider()
    st.subheader("Informasi Smart Contract")
    st.write("Nama:", deployment["contractName"])
    st.write("Alamat Kontrak:")
    st.code(CONTRACT_ADDRESS)
    st.write("Owner Kontrak:")
    st.code(owner_address)

# ==========================================
# 2. DATA MANAGEMENT
# ==========================================
elif menu == "Data Management":
    page_header("Data Management", "Semua data dibaca langsung dari smart contract.")

    tab_m, tab_r, tab_c = st.tabs(["Merchant", "Reward", "Customer"])

    with tab_m:
        merchants = get_merchants()
        if merchants:
            st.dataframe(pd.DataFrame(merchants), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada merchant.")

    rewards = get_rewards()
    with tab_r:
        if rewards:
            st.dataframe(pd.DataFrame(rewards), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada reward yang diberikan.")

    with tab_c:
        customers = get_customers(rewards)
        if customers:
            st.dataframe(pd.DataFrame(customers), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada customer yang menerima reward.")
        st.caption("Daftar ini berisi customer yang pernah menerima reward "
                   "(kontrak tidak menyimpan array seluruh customer).")

    if st.button("Muat ulang data"):
        st.rerun()

# ==========================================
# 3. FORM INPUT
# ==========================================
elif menu == "Form Input":
    page_header("Form Input", "Tambah data baru ke smart contract. Setiap form divalidasi sebelum dikirim.")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Daftar Customer", "Tambah Merchant", "Berikan Reward", "Tukar Poin"]
    )

    # --- Daftar customer
    with tab1:
        with st.form("register_customer"):
            nama = st.text_input("Nama Customer")
            submit = st.form_submit_button("Daftar Customer")
        if submit:
            if not address:
                st.error("Hubungkan wallet terlebih dahulu.")
            elif not nama.strip():
                st.warning("Nama tidak boleh kosong.")
            elif is_customer:
                st.warning("Wallet ini sudah terdaftar.")
            else:
                send_transaction("daftarCustomerBaru", contract.functions.daftarCustomerBaru(nama.strip()))

    # --- Tambah merchant
    with tab2:
        if address and not is_owner:
            st.warning(f"Hanya owner yang dapat menambah merchant. Owner kontrak: {short(owner_address)}")
        with st.form("add_merchant"):
            merchant_id = st.number_input("ID Merchant", min_value=1, step=1)
            merchant_name = st.text_input("Nama Merchant")
            submit = st.form_submit_button("Tambah Merchant")
        if submit:
            if not address:
                st.error("Hubungkan wallet terlebih dahulu.")
            elif not is_owner:
                st.error("Hanya owner yang dapat menambah merchant.")
            elif not merchant_name.strip():
                st.warning("Nama merchant wajib diisi.")
            elif contract.functions.daftarMerchant(int(merchant_id)).call()[0] != 0:
                st.warning("ID Merchant sudah terdaftar.")
            else:
                send_transaction(
                    "tambahMerchant",
                    contract.functions.tambahMerchant(int(merchant_id), merchant_name.strip()),
                )

    # --- Berikan reward
    with tab3:
        if address and not is_owner:
            st.warning(
                f"Hanya owner yang dapat memberikan reward. "
                f"Ganti akun MetaMask ke owner kontrak: {short(owner_address)}"
            )
        with st.form("give_reward"):
            customer_address = st.text_input("Alamat Wallet Customer")
            merchant_id = st.number_input("ID Merchant", min_value=1, step=1, key="rw_mid")
            transaction_id = st.text_input("ID Transaksi")
            jumlah = st.number_input("Jumlah Poin", min_value=1, step=1)
            submit = st.form_submit_button("Berikan Reward")
        if submit:
            if not address:
                st.error("Hubungkan wallet terlebih dahulu.")
            elif not is_owner:
                st.error("Hanya owner yang dapat memberikan reward.")
            elif not Web3.is_address(customer_address):
                st.error("Alamat wallet customer tidak valid.")
            elif not transaction_id.strip():
                st.warning("ID Transaksi wajib diisi.")
            else:
                cust = Web3.to_checksum_address(customer_address)
                if contract.functions.daftarCustomer(cust).call()[0] == ZERO:
                    st.error("Customer belum terdaftar. Minta customer mendaftar dulu di tab Daftar Customer.")
                elif contract.functions.daftarMerchant(int(merchant_id)).call()[0] == 0:
                    st.error("Merchant tidak ditemukan.")
                else:
                    send_transaction(
                        "berikanReward",
                        contract.functions.berikanReward(
                            cust, int(merchant_id), transaction_id.strip(), int(jumlah)
                        ),
                    )

    # --- Tukar poin
    with tab4:
        if not address:
            st.info("Hubungkan wallet untuk menukar poin.")
        else:
            saldo = contract.functions.saldoPoinCustomer(address).call()
            st.metric("Saldo Poin", f"{saldo} LRT")
            with st.form("redeem_points"):
                jumlah_tukar = st.number_input("Jumlah poin yang ditukar", min_value=1, step=1)
                submit = st.form_submit_button("Tukar Poin")
            if submit:
                if not is_customer:
                    st.error("Wallet ini belum terdaftar sebagai customer.")
                elif jumlah_tukar > saldo:
                    st.error("Saldo poin tidak mencukupi.")
                else:
                    send_transaction("tukarPoin", contract.functions.tukarPoin(int(jumlah_tukar)))

# ==========================================
# 4. DETAIL DATA
# ==========================================
elif menu == "Detail Data":
    page_header("Detail Data", "Lihat detail merchant atau reward berdasarkan ID unik.")
    tab_m, tab_r = st.tabs(["Detail Merchant", "Detail Reward (NFT)"])

    with tab_m:
        mid = st.number_input("ID Merchant", min_value=1, step=1, key="detail_mid")
        if st.button("Lihat Merchant"):
            m = contract.functions.daftarMerchant(int(mid)).call()
            if m[2]:
                st.success("Merchant ditemukan.")
                a, b = st.columns(2)
                a.metric("ID", m[0])
                b.metric("Nama", m[1])
                jml = [r for r in get_rewards() if r["Merchant ID"] == int(mid)]
                st.write("Jumlah reward dari merchant ini:", len(jml))
            else:
                st.warning("Merchant tidak ditemukan.")

    with tab_r:
        token_id = st.number_input("Token ID", min_value=1, step=1, key="detail_tid")
        if st.button("Lihat Reward"):
            try:
                r = contract.functions.getReward(int(token_id)).call()
                nft_owner = contract.functions.getOwner(int(token_id)).call()
                st.success("Data reward ditemukan.")
                c1, c2 = st.columns(2)
                c1.metric("Token ID", r[0])
                c2.metric("Jumlah Poin", f"{r[4]} LRT")
                st.write("Customer:", r[1])
                st.write("Pemilik NFT saat ini:", nft_owner)
                st.write("Merchant ID:", r[2])
                st.write("Transaction ID:", r[3])
                st.write("Waktu:", datetime.fromtimestamp(r[5]).strftime("%Y-%m-%d %H:%M:%S"))
            except Exception:
                st.error("Data reward tidak ditemukan.")

# ==========================================
# 5. WALLET & TRANSACTION
# ==========================================
elif menu == "Wallet & Transaction":
    page_header("Wallet & Transaction", "Informasi wallet yang terhubung dan status transaksi pada sesi ini.")

    if address:
        st.subheader("Alamat Wallet")
        st.code(address)

        c1, c2, c3 = st.columns(3)
        with c1:
            card("Saldo ETH", f"{float(w3.from_wei(w3.eth.get_balance(address), 'ether')):.4f}", "ETH")
        with c2:
            card("Saldo Poin", contract.functions.saldoPoinCustomer(address).call(), "LRT")
        with c3:
            card("Peran", "Owner" if is_owner else "Customer" if is_customer else "Belum terdaftar", "Di kontrak")

        if is_customer:
            nama_cust = contract.functions.daftarCustomer(address).call()[1]
            st.success(f"Terdaftar sebagai customer: {nama_cust}")
        else:
            st.info("Wallet ini belum terdaftar sebagai customer.")
    else:
        st.info("Hubungkan wallet yang berada di jaringan Hardhat untuk melihat informasi.")

    st.divider()
    st.subheader("Status Transaksi (sesi ini)")
    if st.session_state.tx_log:
        st.dataframe(pd.DataFrame(st.session_state.tx_log), use_container_width=True, hide_index=True)
    else:
        st.caption("Belum ada transaksi pada sesi ini.")

# ==========================================
# FOOTER
# ==========================================
st.divider()
st.caption("Loyalty Reward System | Powered by Solidity, Hardhat & Web3.py")