#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════
#  Wallet Scanner Test Suite Generator
# ═══════════════════════════════════════════════════════════
#
#  Erstellt realistische Test-Dateien für Wallet-Scanner
#  mit verschiedenen Wallet-Typen und Seed-Phrases
#
# ═══════════════════════════════════════════════════════════

TEST_ROOT="${1:-$HOME/wallet_scanner_test}"

echo "═══════════════════════════════════════════════════════════"
echo " 🧪 Wallet Scanner Test Suite Generator"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Erstelle Test-Struktur in: $TEST_ROOT"
echo ""

# Verzeichnis erstellen
mkdir -p "$TEST_ROOT"
cd "$TEST_ROOT"

# ═══════════════════════════════════════════════════════════
#  1. BITCOIN CORE WALLETS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Bitcoin Core Wallets..."
mkdir -p bitcoin_core/.bitcoin

# wallet.dat (klassisches Format)
cat > bitcoin_core/.bitcoin/wallet.dat << 'EOF'
# Bitcoin Core Wallet (Testdatei)
# Enthält gefälschte Keys für Testing

wallet_version=60000
minversion=60000

# Gefälschter Private Key (HEX)
private_key=5J3mBbAH58CpQ3Y5RNJpUKPE62SQ5tfcvU2JpbnkeyhfsYB1Jcn

# Gefälschter Public Key
public_key=04678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5f

# Wallet Creation Time
wallet_created=1609459200

# Seed (base58)
seed=xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi
EOF

# wallet (neueres Format ohne .dat)
cat > bitcoin_core/.bitcoin/wallet << 'EOF'
# Bitcoin Core Wallet v2 (Testdatei)

version=2
encrypted=false

# BIP39 Seed
seed_hex=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

# Derivation Path
path=m/44'/0'/0'/0/0

# Test Private Key
privkey=L5EZftvrYaSudiozVRzTqLcHLNDoVn7H5HSfM9BAN6tMJX8oTWz6
EOF

# ═══════════════════════════════════════════════════════════
#  2. ETHEREUM KEYSTORES
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Ethereum Keystores..."
mkdir -p ethereum/.ethereum/keystore

# UTC Keystore Format
cat > ethereum/.ethereum/keystore/UTC--2024-01-01T00-00-00.000000000Z--abcdef1234567890abcdef1234567890abcdef12 << 'EOF'
{
  "version": 3,
  "id": "12345678-1234-1234-1234-123456789abc",
  "address": "abcdef1234567890abcdef1234567890abcdef12",
  "crypto": {
    "ciphertext": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "cipherparams": {
      "iv": "0123456789abcdef0123456789abcdef"
    },
    "cipher": "aes-128-ctr",
    "kdf": "scrypt",
    "kdfparams": {
      "dklen": 32,
      "salt": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
      "n": 262144,
      "r": 8,
      "p": 1
    },
    "mac": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
  }
}
EOF

# keystore.json (alternatives Format)
cat > ethereum/.ethereum/keystore.json << 'EOF'
{
  "version": 3,
  "id": "98765432-9876-9876-9876-987654321098",
  "address": "1234567890abcdef1234567890abcdef12345678",
  "crypto": {
    "ciphertext": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
    "cipherparams": {
      "iv": "abcdef0123456789abcdef0123456789"
    },
    "cipher": "aes-128-ctr",
    "kdf": "pbkdf2",
    "kdfparams": {
      "dklen": 32,
      "salt": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "c": 262144,
      "prf": "hmac-sha256"
    },
    "mac": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
  }
}
EOF

# ═══════════════════════════════════════════════════════════
#  3. SEED PHRASES (BIP39)
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Seed Phrase Dateien..."
mkdir -p seeds

# 12-word seed
cat > seeds/seed_12_words.txt << 'EOF'
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about
EOF

# 24-word seed
cat > seeds/seed_24_words.txt << 'EOF'
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art
EOF

# Recovery phrase (mit Zusatzinfo)
cat > seeds/recovery_phrase.txt << 'EOF'
# Wallet Recovery Information
# Created: 2024-01-01
# Type: BIP39 24-word seed

Seed Phrase:
witch collapse practice feed shame open despair creek road again ice least

Passphrase: (optional)
mySecretPassphrase123

Derivation Path:
m/44'/60'/0'/0

First Address:
0x1234567890AbcdEF1234567890aBcdef12345678
EOF

# mnemonic.txt (gemischt mit anderen Infos)
cat > seeds/mnemonic.txt << 'EOF'
My Crypto Wallet Backup - KEEP SAFE!

Generated: 2023-06-15
Wallet: MetaMask

Mnemonic (12 words):
army van defense carry jealous true garbage claim echo media make crunch

NEVER share this with anyone!
Store in multiple safe locations.

Wallet Address: 0xabcd...1234
EOF

# ═══════════════════════════════════════════════════════════
#  4. ELECTRUM WALLETS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Electrum Wallets..."
mkdir -p electrum/.electrum/wallets

cat > electrum/.electrum/wallets/default_wallet << 'EOF'
{
  "wallet_type": "standard",
  "use_encryption": false,
  "seed": "legal winner thank year wave sausage worth useful legal winner thank yellow",
  "seed_type": "electrum",
  "keystore": {
    "type": "bip32",
    "xprv": "xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73",
    "xpub": "xpub661MyMwAqRbcEYS8w7XLSVeEsBXy79zSzH1J8vCdxAZningWLdN3zgtU6LBpB85b3D2yc8sfvZU521AAwdZafEz7mnzBBsz4wKY5fTtTQBm"
  }
}
EOF

# ═══════════════════════════════════════════════════════════
#  5. PRIVATE KEYS (verschiedene Formate)
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Private Key Dateien..."
mkdir -p private_keys

# WIF Format (Bitcoin)
cat > private_keys/bitcoin_private.key << 'EOF'
# Bitcoin Private Key (WIF Format)
5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ
EOF

# Hex Format
cat > private_keys/ethereum_private.key << 'EOF'
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
EOF

# PEM Format
cat > private_keys/rsa_private.pem << 'EOF'
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7VJTUt9Us8cKj
MzEfYyjiWA4R4/M2bS1+fWIcPm15A8+raZ4dp8vBAdFmXjNAf0tHJXdqgV5bGPz
-----END PRIVATE KEY-----
EOF

# ═══════════════════════════════════════════════════════════
#  6. WALLET SOFTWARE CONFIGS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Wallet Konfigurationen..."
mkdir -p configs

cat > configs/bitcoin.conf << 'EOF'
# Bitcoin Core Configuration
rpcuser=bitcoinrpc
rpcpassword=secretpassword123
rpcport=8332
server=1
txindex=1

# Wallet
wallet=main_wallet
keypool=100

# Test Private Key (DO NOT USE IN PRODUCTION!)
# 5KYZdUEo39z3FPrtuX2QbbwGnNP5zTd7yyr2SC1j299sBCnWjss
EOF

cat > configs/ethereum_config.json << 'EOF'
{
  "network": "mainnet",
  "rpc": "http://localhost:8545",
  "accounts": [
    {
      "address": "0x1234567890abcdef1234567890abcdef12345678",
      "privateKey": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    }
  ]
}
EOF

# ═══════════════════════════════════════════════════════════
#  7. METAMASK / BROWSER EXTENSION DATA
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Browser Extension Daten..."
mkdir -p browser_data/metamask

cat > browser_data/metamask/vault.json << 'EOF'
{
  "data": "7b2276657273696f6e223a332c226964223a2231323334353637382d313233342d313233342d313233342d313233343536373839616263222c2261646472657373223a22616263646566313233343536373839306162636465663132333435363738393061626364656631322c22637279",
  "iv": "0123456789abcdef0123456789abcdef",
  "salt": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210"
}
EOF

# ═══════════════════════════════════════════════════════════
#  8. MONERO / PRIVACY COINS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Monero Wallets..."
mkdir -p monero/.bitmonero

cat > monero/.bitmonero/wallet.keys << 'EOF'
# Monero Wallet Keys (Test Data)
spend_key=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
view_key=fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210

# Mnemonic Seed (25 words)
abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey abbey
EOF

# ═══════════════════════════════════════════════════════════
#  9. LITECOIN / ALTCOINS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle Altcoin Wallets..."
mkdir -p altcoins/.litecoin

cat > altcoins/.litecoin/wallet.dat << 'EOF'
# Litecoin Core Wallet (Test)
version=1
private_key=6u7VV3nqh7uQDNqPMqJZqLhYgbDYqqpuPZuqWpQBJFQ3QLZQjPG
address=LYWKqJhtPeGyBAw7WC8R3F7ovxtzAiubdM
EOF

# ═══════════════════════════════════════════════════════════
#  10. DOGECOIN
# ═══════════════════════════════════════════════════════════

mkdir -p altcoins/.dogecoin

cat > altcoins/.dogecoin/wallet.dat << 'EOF'
# Dogecoin Wallet (Much Test! Very Secure!)
wow_private_key=QPkeC7hJSJH5cVBW8qZqKVKhQVVKVKhQVVKVKh
such_address=DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L
EOF

# ═══════════════════════════════════════════════════════════
#  11. FALSCHE POSITIVE (Sollten NICHT erkannt werden)
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle False-Positive Tests..."
mkdir -p false_positives

cat > false_positives/not_a_wallet.dat << 'EOF'
This file is named wallet.dat but contains no wallet data.
Just some random text to test the scanner's content filtering.
No private keys here! Move along!
EOF

cat > false_positives/seed_package.txt << 'EOF'
# Garden Seed Package Information
# Not a crypto seed!

Tomato Seeds: 50 seeds
Carrot Seeds: 100 seeds
Lettuce Seeds: 75 seeds

Planting Instructions:
1. Plant seeds 1 inch deep
2. Water regularly
3. Harvest after 60 days
EOF

cat > false_positives/keystore.txt << 'EOF'
The keystore at the local shop sells spare keys.
Not related to cryptocurrency at all!
EOF

# ═══════════════════════════════════════════════════════════
#  12. NESTED DIRECTORIES (Versteckte Wallets)
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle verschachtelte Strukturen..."
mkdir -p deep/nested/hidden/backup/.wallets

cat > deep/nested/hidden/backup/.wallets/.secret_seed << 'EOF'
# Deeply nested wallet seed (should still be found!)
test test test test test test test test test test test junk
EOF

# ═══════════════════════════════════════════════════════════
#  13. VERSCHIEDENE ENCODINGS
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle verschiedene Encodings..."
mkdir -p encodings

# Base64 encoded seed
cat > encodings/seed_base64.txt << 'EOF'
# Base64 encoded seed phrase
YWJhbmRvbiBhYmFuZG9uIGFiYW5kb24gYWJhbmRvbiBhYmFuZG9uIGFiYW5kb24gYWJhbmRvbiBhYmFuZG9uIGFiYW5kb24gYWJhbmRvbiBhYmFuZG9uIGFib3V0
EOF

# Hex encoded private key
cat > encodings/privkey_hex.txt << 'EOF'
Private Key (hex):
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
EOF

# ═══════════════════════════════════════════════════════════
#  14. UMBENENNTE DATEIEN
# ═══════════════════════════════════════════════════════════

echo "📁 Erstelle umbenannte Wallet-Dateien..."
mkdir -p renamed

# Wallet als .txt getarnt
cat > renamed/my_notes.txt << 'EOF'
# This is actually a wallet seed disguised as notes
legal winner thank year wave sausage worth useful legal winner thank yellow
EOF

# Wallet als .bak
cat > renamed/old_wallet.bak << 'EOF'
{
  "version": 3,
  "crypto": {
    "ciphertext": "test123456789abcdef",
    "kdf": "scrypt"
  }
}
EOF

# ═══════════════════════════════════════════════════════════
#  15. ZUSAMMENFASSUNG & TEST-INFO
# ═══════════════════════════════════════════════════════════

cat > README_TEST_SUITE.md << 'EOF'
# Wallet Scanner Test Suite

Diese Test-Suite enthält **realistische Test-Dateien** für Wallet-Scanner.

## ⚠️ WICHTIG: NUR TEST-DATEN!

**ALLE Keys, Seeds und Adressen sind GEFÄLSCHT!**
- Keine echten Private Keys
- Keine echten Seed Phrases  
- Keine echten Wallet-Daten
- **NIEMALS echte Wallets hier ablegen!**

## Verzeichnis-Struktur

```
wallet_scanner_test/
├── bitcoin_core/          # Bitcoin Core Wallets
│   └── .bitcoin/
│       ├── wallet.dat     # Klassisches Format
│       └── wallet         # Neues Format
│
├── ethereum/              # Ethereum Keystores
│   └── .ethereum/
│       └── keystore/
│           ├── UTC--*     # UTC Keystore Format
│           └── keystore.json
│
├── seeds/                 # BIP39 Seed Phrases
│   ├── seed_12_words.txt  # 12-word seed
│   ├── seed_24_words.txt  # 24-word seed
│   ├── recovery_phrase.txt
│   └── mnemonic.txt
│
├── electrum/              # Electrum Wallets
│   └── .electrum/
│       └── wallets/
│           └── default_wallet
│
├── private_keys/          # Private Keys (verschiedene Formate)
│   ├── bitcoin_private.key    # WIF
│   ├── ethereum_private.key   # Hex
│   └── rsa_private.pem        # PEM
│
├── configs/               # Wallet Konfigurationen
│   ├── bitcoin.conf
│   └── ethereum_config.json
│
├── browser_data/          # Browser Extension Daten
│   └── metamask/
│       └── vault.json
│
├── monero/                # Monero Wallets
│   └── .bitmonero/
│       └── wallet.keys
│
├── altcoins/              # Altcoin Wallets
│   ├── .litecoin/
│   └── .dogecoin/
│
├── false_positives/       # Sollten NICHT erkannt werden
│   ├── not_a_wallet.dat
│   ├── seed_package.txt
│   └── keystore.txt
│
├── deep/nested/hidden/    # Versteckte Wallets (tief verschachtelt)
│   └── backup/.wallets/
│       └── .secret_seed
│
├── encodings/             # Verschiedene Encodings
│   ├── seed_base64.txt
│   └── privkey_hex.txt
│
└── renamed/               # Umbenannte Wallet-Dateien
    ├── my_notes.txt       # Wallet als .txt getarnt
    └── old_wallet.bak     # Wallet als .bak

```

## Erwartete Scanner-Ergebnisse

### ✅ Sollten erkannt werden (19 Dateien):

1. `bitcoin_core/.bitcoin/wallet.dat` - Bitcoin Core klassisch
2. `bitcoin_core/.bitcoin/wallet` - Bitcoin Core neu
3. `ethereum/.ethereum/keystore/UTC--*` - Ethereum Keystore
4. `ethereum/.ethereum/keystore.json` - Ethereum Keystore alt
5. `seeds/seed_12_words.txt` - 12-word BIP39
6. `seeds/seed_24_words.txt` - 24-word BIP39
7. `seeds/recovery_phrase.txt` - Recovery mit Info
8. `seeds/mnemonic.txt` - Mnemonic mit Text
9. `electrum/.electrum/wallets/default_wallet` - Electrum
10. `private_keys/bitcoin_private.key` - WIF Private Key
11. `private_keys/ethereum_private.key` - Hex Private Key
12. `configs/bitcoin.conf` - Bitcoin Config mit Key
13. `configs/ethereum_config.json` - ETH Config mit Key
14. `browser_data/metamask/vault.json` - MetaMask Vault
15. `monero/.bitmonero/wallet.keys` - Monero Keys
16. `altcoins/.litecoin/wallet.dat` - Litecoin Wallet
17. `altcoins/.dogecoin/wallet.dat` - Dogecoin Wallet
18. `deep/nested/hidden/backup/.wallets/.secret_seed` - Versteckt
19. `renamed/my_notes.txt` - Getarnt als Notes

### ❌ Sollten NICHT erkannt werden (False Positives):

- `false_positives/not_a_wallet.dat` - Nur Name, kein Inhalt
- `false_positives/seed_package.txt` - Garten-Samen, keine Crypto
- `false_positives/keystore.txt` - Schlüsseldienst, kein Wallet

### 🤔 Abhängig vom Scanner:

- `encodings/seed_base64.txt` - Nur mit Base64-Decoder
- `encodings/privkey_hex.txt` - Nur mit Hex-Pattern
- `private_keys/rsa_private.pem` - Kein Crypto-Wallet (RSA)
- `renamed/old_wallet.bak` - Content-Scan erforderlich

## Test-Befehle

### Mit GUI:
```bash
python3 /path/to/wallet_gui.py
# ROOT: /path/to/wallet_scanner_test
# TARGET: /path/to/wallet_scanner_test
# Scanner auswählen und starten
```

### Standalone CLI:
```bash
python3 /path/to/hrm_swarm_scanner.py \
  --root ~/wallet_scanner_test \
  --target ~/wallet_scanner_test \
  --threads 4 \
  --prefer-rg
```

### Aggressive Mode (mehr False Positives):
```bash
python3 /path/to/wallet_gui.py
# ☑ Aggressiv aktivieren
# Mehr Kandidaten, längere Scan-Zeit
```

## Erwartete Performance

- **File Enumeration:** ~0.01-0.05s (31 Dateien)
- **Content Scan:** ~0.1-1s (19 Kandidaten)
- **Total:** ~0.2-1.5s (abhängig von System)

## Validierung

Nach dem Scan prüfen:

```bash
# Ergebnisse ansehen
cat ~/wallet_scanner_test/_logs/walletscan_*/hits.txt

# Sollte ~19 Hits enthalten
wc -l ~/wallet_scanner_test/_logs/walletscan_*/hits.txt

# Mnemonics prüfen
cat ~/wallet_scanner_test/_logs/walletscan_*/mnemonic_raw.txt
```

## Nutzung

```bash
# Test-Suite erstellen
bash create_test_wallets.sh

# Oder mit custom Pfad
bash create_test_wallets.sh /tmp/my_test

# Scannen und Ergebnisse prüfen
python3 wallet_gui.py
```

## Hinweise

- Alle Daten sind **fiktiv** und **unsicher**!
- **Niemals** echte Wallet-Daten hier ablegen!
- Test-Suite kann beliebig oft neu generiert werden
- Gut geeignet für Regression-Tests und Performance-Benchmarks

EOF

# ═══════════════════════════════════════════════════════════
#  FERTIG!
# ═══════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════"
echo " ✅ Test-Suite erfolgreich erstellt!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Verzeichnis: $TEST_ROOT"
echo ""
echo "Statistik:"
find "$TEST_ROOT" -type f | wc -l | xargs echo "  - Dateien:"
find "$TEST_ROOT" -type d | wc -l | xargs echo "  - Verzeichnisse:"
du -sh "$TEST_ROOT" | awk '{print "  - Größe: " $1}'
echo ""
echo "📖 Dokumentation: $TEST_ROOT/README_TEST_SUITE.md"
echo ""
echo "🧪 Test starten:"
echo "   python3 wallet_gui.py"
echo "   ROOT: $TEST_ROOT"
echo "   TARGET: $TEST_ROOT"
echo ""
echo "Erwartete Treffer: ~19 Wallet-Dateien"
echo "False Positives: 3 Dateien (sollten ignoriert werden)"
echo ""
