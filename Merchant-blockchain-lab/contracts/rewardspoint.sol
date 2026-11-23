// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// ==========================================
// LIBRARY ERC-721
// ==========================================
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";


contract LoyaltyRewardToken is ERC721 {

    address public owner;

    // ==========================================
    // 1. STRUCT TIPE DATA KUSTOM
    // ==========================================

    struct Customer {
        address wallet;
        string nama;
    }

    struct Merchant {
        uint256 id;
        string nama;
        bool terdaftar;
    }

    struct Reward {
        uint256 tokenId;
        address customer;
        uint256 merchantId;
        string transactionId;
        uint256 jumlahLRT;
        uint256 timestamp;
    }


    // ==========================================
    // CUSTOM ERROR
    // ==========================================

    error HanyaOwner();
    error MerchantTidakAda(uint256 id);
    error CustomerTidakAda(address customer);
    error RewardTidakAda(uint256 tokenId);


    // ==========================================
    // 2. MAPPINGS DAN ARRAYS
    // ==========================================

    mapping(address => Customer) public daftarCustomer;

    mapping(uint256 => Merchant) public daftarMerchant;

    mapping(uint256 => Reward) public daftarReward;

    uint256[] public listIdMerchant;

    uint256[] public listTokenIdReward;

    mapping(address => uint256) public saldoPoinCustomer;


    // ==========================================
    // 3. TOKEN ID
    // ==========================================

    uint256 private nextTokenId = 1;


    // ==========================================
    // 4. EVENTS
    // ==========================================

    event CustomerTerdaftar(
        address indexed customer,
        string nama
    );

    event MerchantDitambahkan(
        uint256 indexed id,
        string nama
    );

    event RewardDiberikan(
        uint256 indexed tokenId,
        address indexed customer,
        uint256 merchantId,
        uint256 jumlahLRT
    );

        event PoinDitukar(
        address indexed customer,
        uint256 jumlahPoin
    );


    // ==========================================
    // 5. CONSTRUCTOR ERC-721
    // ==========================================

    constructor()
        ERC721("Loyalty Reward Token", "LRT")
    {
        owner = msg.sender;
    }


    // ==========================================
    // 6. MODIFIER OWNER
    // ==========================================

    modifier onlyOwner() {

        if (msg.sender != owner)
            revert HanyaOwner();

        _;
    }


    // ==========================================
    // 7. MENDAFTARKAN CUSTOMER
    // ==========================================

    function daftarCustomerBaru(
        string memory _nama
    )
        external
    {

        require(
            bytes(_nama).length > 0,
            "Nama customer wajib diisi"
        );

        daftarCustomer[msg.sender] = Customer({
            wallet: msg.sender,
            nama: _nama
        });

        emit CustomerTerdaftar(
            msg.sender,
            _nama
        );
    }


    // ==========================================
    // 8. MENAMBAHKAN MERCHANT
    // ==========================================

    function tambahMerchant(
        uint256 _id,
        string memory _nama
    )
        external
        onlyOwner
    {

        require(
            daftarMerchant[_id].id == 0,
            "ID Merchant sudah terdaftar"
        );

        require(
            bytes(_nama).length > 0,
            "Nama merchant wajib diisi"
        );

        daftarMerchant[_id] = Merchant({
            id: _id,
            nama: _nama,
            terdaftar: true
        });

        listIdMerchant.push(_id);

        emit MerchantDitambahkan(
            _id,
            _nama
        );
    }


    // ==========================================
    // 9. MEMBERIKAN REWARD + MINT NFT
    // ==========================================

    function berikanReward(
        address _customer,
        uint256 _merchantId,
        string memory _transactionId,
        uint256 _jumlahLRT
    )
        external
        onlyOwner
        returns (uint256)
    {

        // ======================================
        // VALIDASI CUSTOMER
        // ======================================

        if (
            daftarCustomer[_customer].wallet
            == address(0)
        )
            revert CustomerTidakAda(_customer);


        // ======================================
        // VALIDASI MERCHANT
        // ======================================

        if (
            daftarMerchant[_merchantId].id
            == 0
        )
            revert MerchantTidakAda(
                _merchantId
            );


        // ======================================
        // VALIDASI JUMLAH REWARD
        // ======================================

        require(
            _jumlahLRT > 0,
            "Jumlah reward harus lebih dari 0"
        );


        // ======================================
        // AMBIL TOKEN ID
        // ======================================

        uint256 tokenId = nextTokenId;


        // ======================================
        // MINT NFT
        // ======================================

        _safeMint(
            _customer,
            tokenId
        );


        // ======================================
        // TOKEN ID BERIKUTNYA
        // ======================================

        nextTokenId++;


        // ======================================
        // SIMPAN DATA REWARD
        // ======================================

        daftarReward[tokenId] = Reward({
            tokenId: tokenId,
            customer: _customer,
            merchantId: _merchantId,
            transactionId: _transactionId,
            jumlahLRT: _jumlahLRT,
            timestamp: block.timestamp
        });


        // ======================================
        // SIMPAN TOKEN ID
        // ======================================

        listTokenIdReward.push(
            tokenId
        );
        // Menambahkan saldo poin customer
            saldoPoinCustomer[_customer] += _jumlahLRT;


        // ======================================
        // EVENT
        // ======================================

        emit RewardDiberikan(
            tokenId,
            _customer,
            _merchantId,
            _jumlahLRT
        );


        return tokenId;
    }


    // ==========================================
    // 10. CEK PEMILIK NFT
    // ==========================================

    function getOwner(
        uint256 tokenId
    )
        public
        view
        returns (address)
    {

        return ownerOf(tokenId);
    }



    // ==========================================
    // 11. MELIHAT DATA REWARD
    // ==========================================

    function getReward(
        uint256 tokenId
    )
        external
        view
        returns (
            uint256,
            address,
            uint256,
            string memory,
            uint256,
            uint256
        )
    {
        Reward memory reward = daftarReward[tokenId];

        if (reward.tokenId == 0)
            revert RewardTidakAda(tokenId);

        return (
            reward.tokenId,
            reward.customer,
            reward.merchantId,
            reward.transactionId,
            reward.jumlahLRT,
            reward.timestamp
        );

        
    }


    // ==========================================
    // 12. CEK SALDO POIN CUSTOMER
    // ==========================================

    function cekSaldoPoin()
        external
        view
        returns (uint256)
    {
        return saldoPoinCustomer[msg.sender];
    }


    // ==========================================
    // 13. MENUKARKAN POIN CUSTOMER
    // ==========================================

    function tukarPoin(
        uint256 _jumlahPoin
    )
        external
    {
        require(
            daftarCustomer[msg.sender].wallet != address(0),
            "Customer belum terdaftar"
        );

        require(
            _jumlahPoin > 0,
            "Jumlah poin harus lebih dari 0"
        );

        require(
            saldoPoinCustomer[msg.sender] >= _jumlahPoin,
            "Saldo poin tidak mencukupi"
        );

        // Mengurangi saldo poin customer
        saldoPoinCustomer[msg.sender] -= _jumlahPoin;

        // Mencatat aktivitas penukaran
        emit PoinDitukar(
            msg.sender,
            _jumlahPoin
        );
    }

    function getTotalMerchant()
    external
    view
    returns (uint256)
{
    return listIdMerchant.length;
}

} // PENUTUP CONTRACT
