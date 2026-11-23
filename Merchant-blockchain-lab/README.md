# ☕ Loyalty Reward System

Aplikasi web sistem poin loyalitas berbasis blockchain. Smart contract **LoyaltyRewardToken (ERC-721)** dijalankan di jaringan lokal **Hardhat**, dan antarmukanya dibuat dengan **Streamlit** yang terhubung lewat **Web3.py**.

> Tugas Praktikum Blockchain — Modul 11–12: Implementasi UI

## Fitur

- Daftar customer dan tambah merchant
- Memberikan reward (mint NFT + saldo poin) dan menukar poin
- Tabel data merchant, reward, dan customer yang dibaca langsung dari smart contract
- Detail merchant dan reward berdasarkan ID
- Informasi wallet serta status transaksi (menunggu, berhasil, gagal)

## Teknologi

| Bagian | Teknologi |
|---|---|
| Smart contract | Solidity 0.8.20, OpenZeppelin ERC-721 |
| Jaringan lokal | Hardhat |
| Backend app | Python, Web3.py |
| Antarmuka | Streamlit, MetaMask |

## Struktur Proyek

```
Merchant-blockchain-lab/
├── contracts/LoyaltyRewardToken.sol   # smart contract
├── scripts/deploy.js                  # deploy + simpan alamat ke deployment.json
├── app.py                             # aplikasi Streamlit
├── deployment.json                    # dibuat otomatis oleh deploy.js
└── artifacts/                         # dibuat otomatis oleh hardhat compile
```

## Prasyarat

- Node.js dan npm
- Python 3.10+
- Ekstensi MetaMask di browser

## Cara Menjalankan

**1. Instal dependensi**

```bash
npm install
pip install streamlit web3 pandas
```

**2. Jalankan node Hardhat** (Terminal 1, biarkan tetap terbuka)

```bash
npx hardhat node
```

**3. Compile dan deploy kontrak** (Terminal 2)

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

**4. Jalankan aplikasi** (Terminal 3)

```bash
streamlit run app.py
```

Buka `http://localhost:8501`.

## Pengaturan MetaMask

1. Tambahkan jaringan **Hardhat Local**: RPC `http://127.0.0.1:8545`, Chain ID `31337`, simbol `ETH`.
2. Import akun dari daftar **Accounts** di terminal `npx hardhat node`:
   - **Account #0** → owner kontrak (deployer)
   - **Account #1** → customer
3. Klik **Connect MetaMask** di aplikasi.

> Gunakan akun hasil import dari Hardhat. Akun MetaMask biasa tidak dikenali node, sehingga tidak bisa mengirim transaksi.

## Halaman dan Hubungannya dengan Smart Contract

| Halaman | Fungsi | Fungsi kontrak yang dipakai |
|---|---|---|
| Dashboard | Status jaringan dan ringkasan data | `owner`, `getTotalMerchant`, `listTokenIdReward`, `getReward`, `saldoPoinCustomer` |
| Data Management | Tabel merchant, reward, customer | `listIdMerchant`, `daftarMerchant`, `listTokenIdReward`, `getReward`, `daftarCustomer` |
| Form Input | Daftar customer, tambah merchant, beri reward, tukar poin | `daftarCustomerBaru`, `tambahMerchant`, `berikanReward`, `tukarPoin` |
| Detail Data | Detail merchant dan reward per ID | `daftarMerchant`, `getReward`, `getOwner` |
| Wallet & Transaction | Alamat, saldo, peran, log transaksi | `saldoPoinCustomer`, `daftarCustomer`, `owner` |

## Alur Uji Cepat

1. **Account #0** → Form Input → Tambah Merchant (ID 1)
2. **Account #1** → Form Input → Daftar Customer
3. **Account #0** → Form Input → Berikan Reward ke alamat Account #1
4. **Account #1** → Form Input → Tukar Poin
5. Cek hasilnya di Data Management, Detail Data, dan Wallet & Transaction

## Troubleshooting

| Masalah | Penyebab | Solusi |
|---|---|---|
| `BadFunctionCallOutput` atau pesan "Kontrak ... tidak cocok dengan ABI" | `deployment.json` usang: node Hardhat di-restart atau kontrak diubah tanpa deploy ulang | Jalankan `npx hardhat compile`, lalu deploy ulang (langkah 3), kemudian refresh halaman |
| "Hanya owner yang dapat memberikan reward" | Akun MetaMask yang aktif bukan deployer | Ganti ke **Account #0**. Alamat owner yang benar tertera di Dashboard |
| "Akun ini tidak dikenali node Hardhat" | Akun MetaMask bukan akun bawaan Hardhat | Import private key dari daftar Accounts di terminal `hardhat node` |
| "Jaringan MetaMask berbeda dengan Hardhat RPC" | MetaMask tidak di Chain ID 31337 | Pindah ke jaringan Hardhat Local |
| "Customer belum terdaftar" | Penerima reward belum mendaftar | Daftarkan dulu lewat tab Daftar Customer |
| Error ABI tetap muncul setelah deploy ulang | Ada lebih dari satu `LoyaltyRewardToken.json` di `artifacts` | Hapus folder `artifacts` dan `cache`, lalu `npx hardhat compile` ulang |

> Setiap kali `npx hardhat node` di-restart, chain ter-reset. Jalankan deploy ulang dan, jika perlu, reset akun di MetaMask (*Settings → Advanced → Clear activity tab data*).

## Catatan

- Tabel **Customer** hanya berisi customer yang pernah menerima reward, karena kontrak tidak menyimpan array seluruh customer.
- Transaksi ditandatangani oleh node Hardhat (akun *unlocked*), sedangkan MetaMask dipakai untuk mengenali alamat wallet.
- Proyek ini hanya untuk jaringan lokal. Jangan gunakan private key Hardhat di jaringan sungguhan.