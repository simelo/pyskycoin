import skycoin

forceLowS = True

def test_TestSigRecover():
	vs = [
        [
			b"6028b9e3a31c9e725fcbd7d5d16736aaaafcc9bf157dfb4be62bcbcf0969d488",
			b"036d4a36fa235b8f9f815aa6f5457a607f956a71a035bf0970d8578bf218bb5a",
			b"9cff3da1a4f86caf3683f865232c64992b5ed002af42b321b8d8a48420680487",
			b"0",
			b"56dc5df245955302893d8dda0677cc9865d8011bc678c7803a18b5f6faafec08",
			b"54b5fbdcd8fac6468dac2de88fadce6414f5f3afbb103753e25161bef77705a6",
        ],
		[
			b"b470e02f834a3aaafa27bd2b49e07269e962a51410f364e9e195c31351a05e50",
			b"560978aed76de9d5d781f87ed2068832ed545f2b21bf040654a2daff694c8b09",
			b"9ce428d58e8e4caf619dc6fc7b2c2c28f0561654d1f80f322c038ad5e67ff8a6",
			b"1",
			b"15b7e7d00f024bffcd2e47524bb7b7d3a6b251e23a3a43191ed7f0a418d9a578",
			b"bf29a25e2d1f32c5afb18b41ae60112723278a8af31275965a6ec1d95334e840",
        ],
    ]

	xp = public_key = skycoin.secp256k1go.XY()
	_, sig = skycoin.secp256k1go.SignatureCreate()
	_, msg = skycoin.secp256k1go.NumberCreate()
	for v in vs:
		_, r = skycoin.secp256k1go.SignatureGetR(sig)
		skycoin.secp256k1go.NumberSetHex(r , v[0])
		_, s = skycoin.secp256k1go.SignatureGetR(sig)
		skycoin.secp256k1go.NumberSetHex(s , v[1])
		skycoin.secp256k1go.NumberSetHex(msg , v[2])
		rid = int(v[3])
		skycoin.secp256k1go.FieldSetHex(xp.X , v[4])
		skycoin.secp256k1go.FieldSetHex(xp.Y , v[5])

		err, val = skycoin.secp256k1go.SignatureRecover(sig, public_key, msg, rid)
		assert err == skycoin.SKY_OK and val
		assert skycoin.secp256k1go.FieldEquals(xp.X, public_key.X)[0] == skycoin.SKY_OK
		assert skycoin.secp256k1go.FieldEquals(xp.Y, public_key.Y)[0] == skycoin.SKY_OK

		
def test_TestSigVerify():
	key = skycoin.secp256k1go.XY()
	_, sig = skycoin.secp256k1go.SignatureCreate()
	_, msg = skycoin.secp256k1go.NumberCreate()
	skycoin.secp256k1go.NumberSetHex(msg , b"D474CBF2203C1A55A411EEC4404AF2AFB2FE942C434B23EFE46E9F04DA8433CA")
	_, r = skycoin.secp256k1go.SignatureGetR(sig)
	skycoin.secp256k1go.NumberSetHex(r , b"98F9D784BA6C5C77BB7323D044C0FC9F2B27BAA0A5B0718FE88596CC56681980")
	_, s = skycoin.secp256k1go.SignatureGetS(sig)
	skycoin.secp256k1go.NumberSetHex(s , b"E3599D551029336A745B9FB01566624D870780F363356CEE1425ED67D1294480")
	skycoin.secp256k1go.FieldSetHex(key.X , b"7d709f85a331813f9ae6046c56b3a42737abf4eb918b2e7afee285070e968b93")
	skycoin.secp256k1go.FieldSetHex(key.Y , b"26150d1a63b342986c373977b00131950cb5fc194643cad6ea36b5157eba4602")	
	err, val = skycoin.secp256k1go.SignatureVerify(sig, key, msg)
	assert err == skycoin.SKY_OK and val

	skycoin.secp256k1go.NumberSetHex(msg , b"2c43a883f4edc2b66c67a7a355b9312a565bb3d33bb854af36a06669e2028377")
	_, r = skycoin.secp256k1go.SignatureGetR(sig)
	skycoin.secp256k1go.NumberSetHex(r , b"6b2fa9344462c958d4a674c2a42fbedf7d6159a5276eb658887e2e1b3915329b")
	_, s = skycoin.secp256k1go.SignatureGetS(sig)
	skycoin.secp256k1go.NumberSetHex(s , b"eddc6ea7f190c14a0aa74e41519d88d2681314f011d253665f301425caf86b86")

	_, xy = skycoin.base58.String2Hex(b"02a60d70cfba37177d8239d018185d864b2bdd0caf5e175fd4454cc006fd2d75ac")
	skycoin.secp256k1go.XYParsePubkey(key, xy)
	err, val = skycoin.secp256k1go.SignatureVerify(sig, key, msg)
	assert err == skycoin.SKY_OK and val


def test_TestSigSign():
	_, sig = skycoin.secp256k1go.SignatureCreate()
	_, sec = skycoin.secp256k1go.NumberCreate()
	_, msg = skycoin.secp256k1go.NumberCreate()
	_, non = skycoin.secp256k1go.NumberCreate()
	skycoin.secp256k1go.NumberSetHex(sec , b"73641C99F7719F57D8F4BEB11A303AFCD190243A51CED8782CA6D3DBE014D146")
	skycoin.secp256k1go.NumberSetHex(msg , b"D474CBF2203C1A55A411EEC4404AF2AFB2FE942C434B23EFE46E9F04DA8433CA")
	skycoin.secp256k1go.NumberSetHex(non , b"9E3CD9AB0F32911BFDE39AD155F527192CE5ED1F51447D63C4F154C118DA598E")
	err, recid, res = skycoin.secp256k1go.SignatureSign(sig, sec, msg, non)
	assert err == skycoin.SKY_OK and res == 1
	
	if forceLowS:
		assert recid == 0
	else:
		assert recid == 1
	
	skycoin.secp256k1go.NumberSetHex(non , b"98f9d784ba6c5c77bb7323d044c0fc9f2b27baa0a5b0718fe88596cc56681980")
	_, r = skycoin.secp256k1go.SignatureGetR(sig)
	err, val = skycoin.secp256k1go.NumberIsEqual(r, non)
	assert err == skycoin.SKY_OK and val

	if forceLowS:
		assert skycoin.secp256k1go.NumberSetHex(non , b"1ca662aaefd6cc958ba4604fea999db133a75bf34c13334dabac7124ff0cfcc1") == skycoin.SKY_OK
	else:
		assert skycoin.secp256k1go.NumberSetHex(non , b"E3599D551029336A745B9FB01566624D870780F363356CEE1425ED67D1294480") == skycoin.SKY_OK

	_, s = skycoin.secp256k1go.SignatureGetS(sig)
	err, val = skycoin.secp256k1go.NumberIsEqual(s, non)
	assert err == skycoin.SKY_OK and val