import skycoin
import base64
import binascii

# InputTestData contains hashes to be signed
class InputTestData():
	Hashes = []


# SeedTestData contains data generated by Seed
class SeedTestData():
	Seed = []
	Keys = []


# KeysTestData contains address, public key,  secret key and list of signatures
class KeysTestData():
	Address = ""
	Secret = ""
	Public = ""
	Signatures = []


# InputTestDataFromJSON converts InputTestDataJSON to InputTestData
def InputTestDataFromJSON(InputTestDataJSON):
	hashes = []
	for h in InputTestDataJSON.Hashes:
		h2 = skycoin.cipher_SHA256()
		err = skycoin.SKY_cipher_SHA256FromHex(h.encode(), h2) #ok python2
		hashes.append(h2)
		if err != skycoin.SKY_OK:
			return skycoin.SKY_ERROR, None
	return skycoin.SKY_OK, hashes


# KeysTestDataFromJSON converts KeysTestDataJSON to KeysTestData
def KeysTestDataFromJSON(KeysTestDataJSON):
	addres = skycoin.cipher__Address()
	err = skycoin.SKY_cipher_DecodeBase58Address(KeysTestDataJSON["address"].encode(), addres)
	if err != skycoin.SKY_OK:
		return skycoin.SKY_ERROR, None 
	err, hex_str = skycoin.SKY_base58_String2Hex(KeysTestDataJSON["secret"].encode())
	assert err == skycoin.SKY_OK 
	secret_key = skycoin.cipher_SecKey()
	err = skycoin.SKY_cipher_NewSecKey(hex_str, secret_key)
	assert err == skycoin.SKY_OK

	err , secret_key_hex = skycoin.SKY_cipher_SecKey_Hex(secret_key)
	if err != skycoin.SKY_OK:
		return skycoin.SKY_ERROR, None 
	
	err, hex_str = skycoin.SKY_base58_String2Hex(KeysTestDataJSON["public"].encode())
	assert err == skycoin.SKY_OK 
	public_key = skycoin.cipher_PubKey()
	err = skycoin.SKY_cipher_NewPubKey(hex_str, public_key)
	assert err == skycoin.SKY_OK
	
	err , public_key_hex = skycoin.SKY_cipher_PubKey_Hex(public_key)
	if err != skycoin.SKY_OK:
		return skycoin.SKY_ERROR, None 

	r = KeysTestData()
	r.Address = addres
	r.Public = public_key_hex
	r.Secret = secret_key_hex
	r.Signatures = 0
	if KeysTestDataJSON.get("signatures") == None:
		return skycoin.SKY_OK, r
	sigs = []
	if len(KeysTestDataJSON["signatures"]) >= 0:
		for s in KeysTestDataJSON["signatures"]:
			sig_fromHex = skycoin.cipher_Sig()
			err = skycoin.SKY_cipher_SigFromHex(s.encode(), sig_fromHex)
			assert err == skycoin.SKY_OK
			sigs.append(sig_fromHex)
			assert err == skycoin.SKY_OK
	r.Signatures = sigs
	return skycoin.SKY_OK, r


# SeedTestDataFromJSON converts SeedTestDataJSON to SeedTestData
def SeedTestDataFromJSON(SeedTestDataJSON):
	seed = base64.standard_b64decode(SeedTestDataJSON.Seed)
	keys = []
	for kj in SeedTestDataJSON.Keys:
		err, k = KeysTestDataFromJSON(kj)
		if err == skycoin.SKY_ERROR:
			return skycoin.SKY_ERROR, None
		keys.append(k)
	r = SeedTestData()
	r.Seed = seed
	r.Keys = keys
	return skycoin.SKY_OK, r

# ValidateSeedData validates the provided SeedTestData against the current cipher library.
# inputData is required if SeedTestData contains signatures
def ValidateSeedData(SeedTestData = None, InputTestData = None):
	err, keys = skycoin.SKY_cipher_GenerateDeterministicKeyPairs(SeedTestData.Seed, len(SeedTestData.Keys))
	assert err == skycoin.SKY_OK
	if len(SeedTestData.Keys) != len(keys):
		return skycoin.SKY_ERROR
	for i, s in enumerate(keys):
		secret_Key_null = skycoin.cipher_SecKey()
		if s == secret_Key_null:
			return skycoin.SKY_ErrInvalidSecKey
		if (SeedTestData.Keys[i].Secret).decode() != binascii.hexlify(bytearray(s.toStr())).decode('ascii'):
			assert err == skycoin.SKY_ERROR
		p = skycoin.cipher_PubKey()
		p_null = skycoin.cipher_PubKey()
		err = skycoin.SKY_cipher_PubKeyFromSecKey(s, p)
		if p == p_null:
			return skycoin.SKY_ErrInvalidPubKey
		if (SeedTestData.Keys[i].Public).decode() != binascii.hexlify(bytearray(p.toStr())).decode('ascii'):
			return skycoin.SKY_ErrInvalidPubKey
		addr1 = skycoin.cipher__Address()
		addr_null = skycoin.cipher__Address()
		err = skycoin.SKY_cipher_AddressFromPubKey(p, addr1)
		assert err == skycoin.SKY_OK
		if addr1 == addr_null:
			return skycoin.SKY_ErrAddressInvalidPubKey
		if not(SeedTestData.Keys[i].Address == addr1):
			return skycoin.SKY_ErrAddressInvalidChecksum
		addr2 = skycoin.cipher__Address()
		err = skycoin.SKY_cipher_AddressFromSecKey(s, addr2)
		assert err == skycoin.SKY_OK
		if not(addr1 == addr2):
			return skycoin.SKY_ErrAddressInvalidChecksum
		err, validSec = skycoin.SKY_secp256k1_VerifySeckey(s.toStr())
		if validSec != 1:
			return skycoin.SKY_ERROR
		err, validPub = skycoin.SKY_secp256k1_VerifyPubkey(p.toStr())
		if validPub != 1:
			return skycoin.SKY_ERROR


		if InputTestData == None and SeedTestData.Keys[i].Signatures != 0: 
			return skycoin.SKY_ERROR

		if InputTestData != None:
			if len(SeedTestData.Keys[i].Signatures) != len(InputTestData):
				return skycoin.SKY_ERROR
			
			for j in range(len(InputTestData)):
				sig = SeedTestData.Keys[i].Signatures[j]
				sig_null = skycoin.cipher_Sig()
				if sig == sig_null:
					return skycoin.SKY_ERROR

				err = skycoin.SKY_cipher_VerifySignature(p, sig, InputTestData[j])
				if err != skycoin.SKY_OK:
					return skycoin.SKY_ERROR

				err = skycoin.SKY_cipher_ChkSig(addr1, InputTestData[j], sig)
				if err != skycoin.SKY_OK:
					return skycoin.SKY_ERROR

				err = skycoin.SKY_cipher_VerifySignedHash(sig, InputTestData[j])
				if err != skycoin.SKY_OK:
					return skycoin.SKY_ERROR

				p2 = skycoin.cipher_PubKey()
				err = skycoin.SKY_cipher_PubKeyFromSig(sig, InputTestData[j], p2)
				if err != skycoin.SKY_OK:
					return skycoin.SKY_ERROR
				if not(p == p2):
					return 1
					return skycoin.SKY_ERROR

				sig2 = skycoin.cipher_Sig()
				skycoin.SKY_cipher_SignHash(InputTestData[j], s, sig2)
				if sig2 == sig_null:
					return skycoin.SKY_ERROR
	return skycoin.SKY_OK
