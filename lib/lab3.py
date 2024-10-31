import os  # Модуль для работы с файловой системой
import shutil  # Модуль для операций с файлами и директориями
import hashlib  # Модуль для создания хешей
from lab2 import *  # Импорт всех функций из файла lab2 (должен содержать используемые математические функции)

def read_file(file_path, extension):
    full_path = f"{file_path}.{extension}"
    with open(full_path, 'rb') as f:
        return f.read()

# Функция для создания цифровой подписи с использованием алгоритма Эль-Гамаля
def ElGamal_sign(message) -> list:
    generator = 0  # Инициализация генератора для циклической группы
    while True:
        # Генерация простого числа q для создания числа p = 2q + 1
        prime_q = generate_prime(0, 10 ** 9)
        prime_p = 2 * prime_q + 1
        if check_prime(prime_p):  # Проверка, является ли p простым
            break
    print(f"ElGamal parameters: p = {prime_p}, q = {prime_q}")
    
    # Нахождение генератора, удовлетворяющего условиям Эль-Гамаля
    while pow_module(generator, prime_q, prime_p) != 1:
        generator = random.randint(2, prime_p - 1)

    # Генерация закрытого и открытого ключей
    private_key = generate_prime(0, prime_p - 1)
    public_key = pow_module(generator, private_key, prime_p)
    print(f"Keys: Private Key = {private_key}, Public Key = {public_key}")

    # Генерация случайного числа k, которое является взаимно простым с p-1
    coprime_k = generate_coprime(prime_p - 1)
    signature_r = pow_module(generator, coprime_k, prime_p)  # r, одна из частей подписи
    print(f"Signature component r = {signature_r}")
    # Сохранение параметров подписи для проверки
    keys['gamal_sign'] = {'p': prime_p, 'g': generator, 'y': public_key, 'r': signature_r}

    # Вычисление хеша сообщения с помощью MD5
    hash_value = hashlib.md5(message).hexdigest()
    print(f'ElGamal MD5 hash: {hash_value}')
    
    # Преобразование хеша в числовое представление для дальнейших расчетов
    hash_numeric = ''.join(str(pow_module(generator, int(i, 16), prime_p)) for i in hash_value)

    # Вычисление значений u и s для подписи
    u_values = [(int(i, 16) - private_key * signature_r) % (prime_p - 1) for i in hash_value]
    s_values = [(gcd_modified(coprime_k, prime_p - 1)[1] * i) % (prime_p - 1) for i in u_values]
    print(f'ElGamal signature s = {s_values}')

    return s_values  # Возвращение значений s как подписи


# Функция для проверки подписи Эль-Гамаля
def ElGamal_signcheck(message: bytearray, signature: list):
    # Загрузка параметров подписи из сохраненных ключей
    prime_p = keys["gamal_sign"]["p"]
    public_key = keys["gamal_sign"]["y"]
    signature_r = keys["gamal_sign"]["r"]
    generator = keys["gamal_sign"]["g"]

    # Вычисление хеша сообщения с помощью MD5
    hash_value = hashlib.md5(message).hexdigest()
    # Преобразование хеша в числовое представление
    hash_numeric = ''.join(str(pow_module(generator, int(i, 16), prime_p)) for i in hash_value)
    
    # Проверка подписи, сравнение хешей для подтверждения подлинности
    verification_result = ''.join(str(pow_module(public_key, signature_r, prime_p) * pow_module(signature_r, i, prime_p) % prime_p) for i in signature)

    print("ElGamal Verification Result:", "Valid" if verification_result == hash_numeric else "Forgery Detected")


# Функция для создания цифровой подписи с использованием алгоритма RSA
def RSA_sign(message) -> list:
    # Генерация двух случайных простых чисел p и q
    prime_p = generate_prime(0, 10 ** 9)
    prime_q = generate_prime(0, 10 ** 9)
    modulus_n = prime_p * prime_q  # Вычисление модуля n как произведения p и q
    totient_phi = (prime_p - 1) * (prime_q - 1)  # Функция Эйлера от n

    # Генерация закрытого и открытого экспонентов
    private_exponent = generate_coprime(totient_phi)
    public_exponent = gcd_modified(private_exponent, totient_phi)[1]
    if public_exponent < 0:  # Приведение значения в положительный диапазон
        public_exponent += totient_phi
    keys['RSA_sign'] = {'N': modulus_n, 'd': private_exponent}

    # Хеширование сообщения с помощью MD5 и его числовое представление
    hash_value = hashlib.md5(message).hexdigest()
    hash_numeric = ''.join(str(int(i, 16)) for i in hash_value)
    
    # Подпись, которая вычисляется возведением хеша в степень открытого ключа по модулю n
    signature = [pow_module(int(i, 16), public_exponent, modulus_n) for i in hash_value]
    print(f"RSA Signature: {signature}")

    return signature


# Функция для проверки подписи RSA
def RSA_signcheck(message: bytearray, signature: list):
    # Загрузка закрытой экспоненты и модуля n
    private_exponent = keys["RSA_sign"]["d"]
    modulus_n = keys["RSA_sign"]["N"]
    
    # Вычисление хеша сообщения и его числовое представление
    hash_value = hashlib.md5(message).hexdigest()
    hash_numeric = ''.join(str(int(i, 16)) for i in hash_value)
    
    # Проверка подписи путем вычисления обратной операции по закрытому ключу
    verification_result = ''.join(str(pow_module(i, private_exponent, modulus_n)) for i in signature)

    print("RSA Verification Result:", "Valid" if verification_result == hash_numeric else "Forgery Detected")


def GOST_sign(message: bytearray) -> bool:
    # Инициализация простых чисел p и q для алгоритма ГОСТ
    prime_q = random.getrandbits(16)
    multiplier_b = random.getrandbits(16)
    
    # Инициализация prime_p
    prime_p = None
    
    while prime_p is None or not check_prime(prime_p):
        multiplier_b = random.getrandbits(16)
        prime_p = prime_q * multiplier_b + 1

    # Генерация базового элемента a
    generator = random.randint(1, prime_p - 1)
    base_a = pow_module(generator, multiplier_b, prime_p)
    while not base_a > 1:
        generator = random.randint(1, prime_p - 1)
        base_a = pow_module(generator, multiplier_b, prime_p)

    # Генерация закрытого и открытого ключей
    private_key = random.randint(1, prime_q - 1)
    public_key = pow_module(base_a, private_key, prime_p)

    # Вычисление хеша сообщения и его преобразование в целое число
    hash_value = hashlib.md5(message).hexdigest()
    hash_value = int(hash_value, 16)

    # Генерация случайного числа k и вычисление подписи r и s
    signature_r = 0
    signature_s = 0
    while signature_s == 0:
        while signature_r == 0:
            random_k = random.randint(1, prime_q - 1)
            signature_r = pow_module(base_a, random_k, prime_p) % prime_q
        signature_s = (random_k * hash_value + private_key * signature_r) % prime_q

    # Сохранение параметров подписи
    keys['GOST_sign'] = {'q': prime_q, 'a': base_a, 'y': public_key, 'p': prime_p, 'r': signature_r}
    print(f"GOST Signature s = {signature_s}")

    # Запись подписи в файл
    with open(r'..\signs\GOST_sign.txt', 'w') as f:
        f.write(str(signature_s))

    return signature_s


# Функция для проверки подписи ГОСТ
def GOST_signcheck(message: bytearray, signature: list):
    # Загрузка параметров из сохраненных ключей
    prime_q = keys["GOST_sign"]["q"]
    public_key = keys["GOST_sign"]["y"]
    signature_r = keys["GOST_sign"]["r"]
    base_a = keys["GOST_sign"]["a"]
    prime_p = keys["GOST_sign"]["p"]
    
    # Хеширование сообщения
    hash_value = hashlib.md5(message).hexdigest()

    # Вычисление временного значения и параметров для проверки подписи
    temp = gcd_modified(hash_value, prime_q)[1]
    if temp < 1:
        temp += prime_q

    u1 = (signature * temp) % prime_q
    u2 = (-signature_r * temp) % prime_q
    verification_result = ((pow_module(base_a, u1, prime_p) * pow_module(public_key, u2, prime_p)) % prime_p) % prime_q

    print("GOST Verification Result:", "Valid" if verification_result == signature_r else "Forgery Detected")


# Главная часть программы
if __name__ == '__main__':
    try:
        shutil.rmtree(r'..\signs')  # Удаление старой директории подписей, если она существует
    except OSError:
        pass
    os.mkdir(r'..\signs')  # Создание новой директории для хранения подписей

    # Определение базовой директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_filename = os.path.join(current_dir, '..', 'input')
    fake_filename = os.path.join(current_dir, '..', 'input_fake')
    file_extension = 'txt'

    # Чтение содержимого файлов
    try:
        message = read_file(input_filename, file_extension)
        fake_message = read_file(fake_filename, file_extension)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}. Проверьте, что файлы {input_filename}.txt и {fake_filename}.txt существуют.")
        exit()  # Завершение программы, если файлы не найдены

    # Генерация и проверка RSA подписи
    print("Original Message Signature:")
    print(message)
    print()
    rsa_signature = RSA_sign(message)
    with open(r'..\signs\rsa_sign.txt', 'w') as f:
        f.write(str(rsa_signature))
    RSA_signcheck(message, rsa_signature)
    print("\n")

    # Генерация и проверка подписи Эль-Гамаля
    print("ElGamal Signature:")
    elgamal_signature = ElGamal_sign(message)
    with open(r'..\signs\elgamal_sign.txt', 'w') as f:
        f.write(str(elgamal_signature))
    ElGamal_signcheck(message, elgamal_signature)
    print("\n")

    # Генерация и проверка подписи ГОСТ
    print("GOST Signature:")
    gost_signature = GOST_sign(message)

    # Создание файла Input_sign.txt с оригинальным сообщением и подписями
    with open(os.path.join(current_dir, '..', 'Input_sign.txt'), 'wb') as f:
        with open(os.path.join(current_dir, '..', 'Input_sign.txt'), 'w', encoding='utf-8') as f:
            f.write("Original Message:\n")
            f.write(message.decode('utf-8', errors='replace') + "\n\n")  # Предполагаем, что message это байты
            f.write("RSA Signature:\n")
            f.write(str(rsa_signature) + "\n\n")  # Добавление подписи
            f.write("ElGamal Signature:\n")
            f.write(str(elgamal_signature) + "\n\n")
            f.write("GOST Signature:\n")
            f.write(str(gost_signature) + "\n")

    print("Signatures saved to Input_sign.txt")