import sys
sys.path.append('C:WORK/sibguti/7 semestr/InformationProtection/LAB2/lab1.py')
from lab1 import *
import os
import shutil

keys = {}


# генерируем взаимно-простое число
def generate_coprime(p):
    result = random.randint(2, p)
    # print(result)
    while gcd(p, result) != 1:
        result = random.randint(2, p)
        # print(result)
    return result


# шифр Шамира
def Shamir_encode(m) -> list:
    result = list()

    p = generate_prime(0, 10 ** 9)
    print("p = ", p)
    Ca = generate_coprime(p - 1)
    print("Ca = ", Ca)
    Da = gcd_modified(p - 1, Ca)[2]
    if Da < 0:
        Da += p - 1
    print("Da = ", Da)

    Cb = generate_coprime(p - 1)
    print("Cb = ", Cb)
    Db = gcd_modified(p - 1, Cb)[2]
    if Db < 0:
        Db += p - 1
    print("Db = ", Db)
    keys['shamir'] = {'p': p, 'Ca': Ca, 'Da': Da, 'Cb': Cb, 'Db': Db}

    for part in m:
        x1 = pow_module(part, Ca, p)
        x2 = pow_module(x1, Cb, p)
        x3 = pow_module(x2, Da, p)
        result.append(x3)
    return result


# дешифровка Шамира
def Shamir_decode(x3) -> list:
    result = list()
    p = keys["shamir"]["p"]
    Db = keys["shamir"]["Db"]
    for part in x3:
        x4 = pow_module(part, Db, p)
        result.append(x4)
    return result


# шифр Эль-Гамаля
def ElGamal_encode(m) -> list:
    result = list()
    g = 0
    while True:
        q = generate_prime(0, 10 ** 9)
        p = 2 * q + 1
        if check_prime(p):
            break
    print("p = ", p)
    while pow_module(g, q, p) != 1:
        g = random.randint(2, p - 1)

    print("g = ", g)
    x = generate_prime(0, p - 1)
    print("x = ", x)
    y = pow_module(g, x, p)
    print("y = ", y)

    k = generate_prime(0, p - 2)
    print("k = ", k)
    a = pow_module(g, k, p)
    print("a = ", a)

    keys['gamal'] = {'p': p, 'g': g, 'x': x, 'y': y, 'k': k, 'a': a}
    for part in m:
        b = (part * pow_module(y, k, p)) % p
        result.append(b)
    return result


# дешифровка Эль-Гамаля
def ElGamal_decode(b) -> list:
    result = list()
    p = keys["gamal"]["p"]
    x = keys["gamal"]["x"]
    a = keys["gamal"]["a"]
    for part in b:
        m1 = (part * pow_module(a, p - 1 - x, p)) % p
        result.append(m1)
    return result


# шифр RSA
def RSA_encode(m) -> list:
    result = list()

    P = generate_prime(0, 10 ** 9)
    print("P = ", P)
    Q = generate_prime(0, 10 ** 9)
    print("Q = ", Q)
    N = P * Q
    print("N = ", N)
    Phi = (P - 1) * (Q - 1)
    print("Phi = ", Phi)

    d = generate_coprime(Phi)
    print("d = ", d)
    # d = 3
    c = gcd_modified(d, Phi)[1]
    if c < 0:
        c += Phi
    print("c = ", c)

    keys['RSA'] = {'c': c, 'N': N}
    for part in m:
        e = pow_module(part, d, N)
        result.append(e)
    return result


# дешифровка RSA
def RSA_decode(e) -> list:
    result = list()
    c = keys["RSA"]["c"]
    N = keys["RSA"]["N"]
    for part in e:
        m1 = pow_module(part, c, N)
        result.append(m1)
    print("m1 = ", m1)
    return result


# шифр Вернама
def Vernam_encode(m) -> list:
    codes = [random.randint(0, 255) for _ in range(len(m))]
    keys['vernam'] = codes
    return [m[i] ^ codes[i] for i in range(len(m))]


# дешифровка Вернама
def Vernam_decode(e) -> list:
    codes = keys['vernam']
    return [e[i] ^ codes[i] for i in range(len(m))]


# читаем побайтово файлы
def read_file(filename: str, ext: str) -> bytearray:
    with open(filename + '.' + ext, 'rb') as origin_file:
        return bytearray(origin_file.read())


if __name__ == '__main__':
    try:
        shutil.rmtree('..\encode')
    except OSError:
        pass
    os.mkdir('..\encode')

    filename = '.\input'
    ext = 'txt'
    m = read_file(filename, ext)

    sham_enc = Shamir_encode(m)
    #print(sham_enc)
    with open(r'..\encode\shamir_encoded.txt', 'wt') as encode_file:
        encode_file.write(str(sham_enc))
    sham_dec = Shamir_decode(sham_enc)
    #print(bytearray(sham_dec))
    with open(r'..\encode\shamir_decoded.txt', 'wb') as decode_file:
        decode_file.write(bytearray(sham_dec))

    gam_enc = ElGamal_encode(m)
    #print(gam_enc)
    with open(r'..\encode\gamal_encoded.txt', 'wt') as encode_file:
        encode_file.write(str(gam_enc))
    gam_dec = ElGamal_decode(gam_enc)
    #print(bytearray(gam_dec))
    with open(r'..\encode\gamal_decoded.txt', 'wb') as decode_file:
        decode_file.write(bytearray(gam_dec))

    RSA_enc = RSA_encode(m)
    #print(RSA_enc)
    with open(r'..\encode\rsa_encoded.txt', 'wt') as encode_file:
        encode_file.write(str(RSA_enc))
    RSA_dec = RSA_decode(RSA_enc)
    #print(bytearray(RSA_dec))
    with open(r'..\encode\rsa_decoded.txt', 'wb') as decode_file:
        decode_file.write(bytearray(RSA_dec))

    ver_enc = Vernam_encode(m)
    #print(ver_enc)
    with open(r'..\encode\ver_encoded.txt', 'wt') as encode_file:
        encode_file.write(str(ver_enc))
    ver_dec = Vernam_decode(ver_enc)
    #print(bytearray(ver_dec))
    with open(r'..\encode\ver_decoded.txt', 'wb') as decode_file:
        decode_file.write(bytearray(ver_dec))