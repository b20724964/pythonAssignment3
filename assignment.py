import sys
enc_dict, dec_dict = {}, {}
plain_list, cipher_list, key_list = [], [], []

for count, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ "):  # harfeleri numaralanadırmak ve
    enc_dict[letter] = count + 1                                # numaraları harlendirmek için
    dec_dict[count + 1] = letter

for count, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):  #küçük harfeleri de numaralanadırmak için
    enc_dict[letter] = count + 1

try:
    assert len(sys.argv) == 5, "Error: You must enter 4 parameters"
    assert sys.argv[1] in ("enc", "dec"), "Error: Undefined parameter. Please write 'dec' or 'enc'"
    key_format = sys.argv[2].split(".")
    assert key_format[-1] == "txt", f"Error: Key file '{sys.argv[2]}'  could not be read. It must be txt file"
    input_format = sys.argv[3].split(".")
    assert input_format[-1] == "txt", f"Error: Input file '{sys.argv[3]}'  could not be read. It must be txt file"
    f = open(sys.argv[2], "r")
    key_list = [i.strip("\n").split(",") for i in f.readlines()]
    f.close()
    assert len(key_list) != 0, "Key file is empty"
    try:
        for i in range(len(key_list)):
            for j in range(len(key_list[i])):
                key_list[i][j] = int(key_list[i][j])
            assert len(key_list[i]) == len(key_list)    # elemalardan biri eksikse Ör: [[1,2,3],[1,2],[4,5,6]]
    except:                                             # yada kare matrix değilse
        print("Error: Invalid character in Key file!")  # 3 üst satırdaki int e cevirme hatasını yakalamak için
        exit()                                          # python3 de types.IntType çalışmıyormuş yada
    if sys.argv[1] == "enc":                            # ben çalıştıramadım başka türlü bulamadım*
        f = open(sys.argv[3], "r")
        plain_list = [i for i in f.read()]
        f.close()
        assert len(plain_list) != 0, "Input file is empty"
        for i, value in enumerate(plain_list):
            assert value in enc_dict, f"Error: Invalid character in Input file"
            plain_list[i] = enc_dict[value]
    if sys.argv[1] == "dec":
        f = open(sys.argv[3], "r")
        cipher_list = f.read().split(",")
        f.close()
        assert cipher_list[0] != "", "Ciphertext file is empty"
        try:
            for i, value in enumerate(cipher_list):
                cipher_list[i] = int(value)
        except:
            print("Error: Invalid character in Ciphertext file") # * lı açıklamadaki ile aynı
            exit()
except AssertionError as message:
    print(message)
    exit()
except FileNotFoundError as e:
    print("Error: Input file not found" if e.filename == sys.argv[3] else "Error: Key file not found")
    exit()


def control_matrix(matrix): # bunu piazzada 0 olmayacak demenizden önce yazmıştım (her ihtimale karşı bıraktım:)
    change_number = 1       # burada matrisin sol çaprazdan sağ çapraza sıfır rakamı varmı diye kontrol ediyor
    for i in range(len(matrix)):  # varsa satırların yeri değişmeli ve her değişen satır için
        if matrix[i][i] == 0:     # matrix komple -1 ile çarpılmalı
            for j in range(i + 1, len(matrix)):
                if matrix[i][j] != 0:
                    matrix[i], matrix[j] = matrix[j], matrix[i]
                    change_number *= -1
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix[i][j] = matrix[i][j] * change_number
    return matrix


def inverse(matrix):  # matrise birim matris ekleyip seçilen elemanın altındakileri ve üstündekileri sıfırlamak için
    for i in range(len(matrix)):
        matrix[i].extend([0]*i + [1] + [0]*(len(matrix)-i-1))
    control_matrix(matrix)
    for i in range(len(matrix)):  # seçişlenin altındakileri sıfırlamak için
        for j in range(i+1, len(matrix)):
            coefficient = matrix[j][i] / matrix[i][i]
            for k in range(len(matrix[j])):
                matrix[j][k] -= coefficient * matrix[i][k]
    for i in range(len(matrix)-1, -1, -1):  # seçilenin üstündekileri sıfırlamak için
        for j in range(i-1, -1, -1):
            coefficient = matrix[j][i] / matrix[i][i]
            for k in range(len(matrix[j])):
                matrix[j][k] -= coefficient * matrix[i][k]
    for i in range(len(matrix)):    # sıfırlama sonrası sadece sol çaprazdan sağ çapraza rakam kalacak bura da
        coefficient = matrix[i][i]  # onları kendilerine bölerek birim matrise ulaşıyoruz
        for k in range(len(matrix[i])):
            matrix[i][k] /= coefficient
    inverse_key = [(matrix[i][len(matrix[i])//2:]) for i in range(len(matrix))]  # baştaki oluşan birim matrisi
    return inverse_key                                                           # silip sonucu buluyoruz


def space_adder(lists, key):  # listeyi key deki elaman sayısına eşitlemek için boşluk ekliyor
    if len(lists) % len(key) != 0:
        for i in range(len(key)-(len(lists) % len(key))):
            lists.append(27)
        return lists


def matrix_mul(list1, list2):
    last = [[0 for _ in range(len(list2[0]))] for _ in range(len(list2))]
    for i in range(len(last)):
        for j in range(len(last[0])):
            for k in range(len(last)):
                last[i][j] += list1[i][k] * list2[k][j]
    return last


if sys.argv[1] == "enc":
    space_adder(plain_list, key_list)
# listeyi parçalara ayırmak için
    plain_list = [plain_list[i:i + len(key_list)] for i in range(0, len(plain_list), len(key_list))]
# listenin satırları ile stunlarını yer değiştiriyoruz ki listenin ve key in lenleri eşit olsun
    plain_list = [[plain_list[j][i] for j in range(len(plain_list))] for i in range(len(plain_list[0]))]
    result = matrix_mul(key_list, plain_list)
# satır ve stununu değiştirdiğimiz listeyi eski haline getiriyoruz
    result = [[result[j][i] for j in range(len(result))] for i in range(len(result[0]))]
# dosyaya yazdırmak için düzenleniyor
    result = [str(result[i][j])+"," for i in range(len(result)) for j in range(len(result[0]))]
    result[-1] = str(result[-1][:-1])
else:
    key_list = inverse(key_list)
    cipher_list = [cipher_list[i:i + len(key_list)] for i in range(0, len(cipher_list), len(key_list))]
    cipher_list = [[cipher_list[j][i] for j in range(len(cipher_list))] for i in range(len(cipher_list[0]))]
    result = matrix_mul(key_list, cipher_list)
    result = [[round(result[j][i]) for j in range(len(result))] for i in range(len(result[0]))]
    result = [dec_dict[result[i][j]] for i in range(len(result)) for j in range(len(result[0]))]
f = open(sys.argv[4], "w")
f.writelines(result)
f.close()
