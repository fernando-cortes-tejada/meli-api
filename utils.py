def replace_special_characters(string: str):
    replaced = ["á", "é", "í", "ó", "ú", "Á", "É", "Í", "Ó", "Ú", "ñ", "Ñ"]
    by = ["a", "e", "i", "o", "u", "A", "E", "I", "O", "U", "n", "N"]
    for i in range(len(replaced)):
        string = string.replace(replaced[i], by[i])
    return string
