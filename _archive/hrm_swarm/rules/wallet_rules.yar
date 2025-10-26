rule Ethereum_JSON_Keystore_V3 {
  strings:
    $a = "crypto"
    $b = "kdf"
    $c = "ciphertext"
    $d = "mac"
  condition:
    all of them
}

rule Electrum_Wallet {
  strings:
    $a = "seed_version"
    $b = "wallet_type"
    $c = "keystore"
  condition:
    2 of ($a,$b,$c)
}
