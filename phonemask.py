import re

def phone_check():
    phone = input("Введите номер: ")
    phones_mask = re.sub(r'\D', '', phone)

    print(f"\"{phones_mask}\"")

    if len(phones_mask) == 11:
        if int(phones_mask[0]) == 7 or int(phones_mask[0]) == 8:
            print("Проверка телефона по маске2: Все ОК")
            return phones_mask
        else:
            print("Номер телефона начинается не с 8 или 7, при этом кол-во цифр равно 11")
            return 0
    elif len(phones_mask) == 10:
        if int(phones_mask[0]) == (9):
            print("Проверка телефона по маске: Все ОК, забыли прописать 7 или 8")
            return phones_mask
        else:
            print("Номер телефона состоит из 10 цифр, при этом номер не начинается с 9")
            return 0
    elif len(phones_mask) > 11:
        print("Номер телефона содержит более 11 цифр, проверьте номер телефона и попробуйте снова")
        return 0
    elif len(phones_mask) < 10:
        print("Номер телефона содержит менее 10 цифр, проверьте номер телефона и попробуйте снова")
        return 0