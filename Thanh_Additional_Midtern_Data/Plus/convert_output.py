import json
import string
import pandas as pd
import ast
import os
import numpy as np
import xlsxwriter as xlsx
import unicodedata

def ocr_json_read(json_file):
    '''
    Read the OCR information

    Parameters
    ----------
        json_file: str
            Path to json file store the OCR result from CLC API
    Returns
    -------
        ocr_info: dict
            The details from OCR response
    '''

    file_name = os.path.basename(json_file)
    file_name = os.path.splitext(file_name)[0]
    with open(json_file, 'r', encoding='utf-8') as file:
        # Load the content of the JSON file into a dictionary
        json_data = json.load(file)
    temp_result = json_data['data']['result_bbox']
    ocr_info = {'file_name': '',
                'details': []}

    # Add more detail tribute for each box
    for box_index in range(len(temp_result)):
        box_confidence = temp_result[box_index][1][1]

        # Remove the box with confidence < 0.55
        if box_confidence < 0.55:
            continue

        box = {'points':temp_result[box_index][0],
               'transcription':temp_result[box_index][1][0].strip()}

        box['mid'] = np.mean(box['points'], axis=0)
        points = np.array(box['points'])

        # Length of box vertically
        box_length_v = np.linalg.norm(points[3] - points[0])
        # Length of box horizontally
        box_length_h = np.linalg.norm(points[1] - points[0])

        # Flag check valid box
        flag = 1
        if box_length_v > box_length_h:
            word_size = box_length_v / len(box['transcription'])

            # If estimated size of word > or < 2 time of other length then box is invalid
            if word_size//box_length_h > 1 or box_length_h//word_size > 1:
                flag = 0
        else:
            word_size = box_length_h / len(box['transcription'])

            # If estimated size of word > or < 2 time of other length then box is invalid
            if word_size//box_length_v > 1 or box_length_v//word_size > 1:
                flag = 0

        if flag:
            box['word_size'] = word_size
        else:
            box['word_size'] = -1
        ocr_info['details'].append(box)

    ocr_info['file_name'] = file_name

    return ocr_info

def extractText(pdf_file):
    '''
    Read the Quoc Ngu full text and word by word store in txt file.

    Parameters
    ----------
        pdf_file: str
            Path to the Quoc Ngu transcription folder with the name of the PDF
    Returns
    -------
        word_text: list
            Store the word by word sentences in each page as word token
        full_text: list
            Store the full sentences in each page as word token
    '''

    word_text = []
    full_text = []
    file_name = os.path.splitext(pdf_file)[0]
    word_text_file = file_name + "_word.txt"
    full_text_file = file_name + "_text.txt"


    # Read word_text from word_text_file
    with open(word_text_file, "r", encoding="utf-8") as pt_file:
        for line in pt_file:
            # Split the line into words (space-separated) and append to word_text
            word_text += line.strip().split() # Split by space

    # Read full_text from full_text_file
    temp_full_text = []
    with open(full_text_file, "r", encoding="utf-8") as ft_file:
        for line in ft_file:
            line = line.strip('\n')
            temp_full_text += line.split(' ')
    for word in temp_full_text:
        if word in string.punctuation:
            if full_text:
                full_text[-1] += word
        else:
            full_text.append(word)

    return word_text, full_text

def similarRead(file_path):
    '''
    Read Similar Dictionary

    Parameters
    ----------
        file_path: str
            Path to SinoNom_similar_Dic.xlsx

    Returns
    -------
        similar_dic: dict
            Dictionary of Similar Dictionary
            - key: the OCR-ed character
            - value: list of similar Han-Nom characters
    '''
    print(f"[+] Loading {file_path}")
    similar_dict = {}
    try:
        dic = pd.read_excel(file_path)

        dic['Top 20 Similar Characters'] = dic['Top 20 Similar Characters'].apply(ast.literal_eval)
        similar_dict = dict(zip(dic['Input Character'], dic['Top 20 Similar Characters']))

        print(f"[+] Loading {file_path} finished")

    except FileNotFoundError:
        print(f"Error:{file_path} not found.")
    except IOError:
        print(f"Error: Could not open {file_path}.")
    return similar_dict

def quoc_ngu_word_normalize(word):
    '''
    Normalize the style of Quoc Ngu into one united form

    Parameters
    ----------
        word: str
            Word needed to be normalized
    Returns
    -------
        rearranged: str
            Normalized word
    '''
    # Normalize the word to NFD
    normalized = unicodedata.normalize('NFD', word)

    # Separate base characters and diacritical marks
    base_chars = []
    marks = []
    for char in normalized:
        if unicodedata.combining(char):  # Check if it's a diacritical mark
            marks.append(char)
        else:
            base_chars.append(char)

    # Sort the diacritical marks
    sorted_marks = sorted(marks)

    # Combine base characters and sorted marks
    rearranged = ''.join(base_chars + sorted_marks)
    return rearranged

def translationRead(file_path):
    '''
    Read Translation Dictionary

    Parameters
    ----------
        file_path: str
            Path to SinoNom_similar_Dic.xlsx

    Returns
    -------
        similar_dic: dict
            Dictionary of Similar Dictionary
            - key: Quoc Ngu Char
            - value: list of corresponded Han-Nom char
    '''
    print(f"[+] Loading {file_path}")
    translation_dic = {}
    try:
        dic = pd.read_excel(file_path)

        translation_dic = {
            quoc_ngu_word_normalize(key): list(group["SinoNom"])
            for key, group in dic.groupby("QuocNgu")
        }
        print(f"[+] Loading {file_path} finished")

    except FileNotFoundError:
        print("Error: Label.txt file not found.")
    except IOError:
        print("Error: Could not open Label.txt.")

    return translation_dic

def boxSort(ocr_data):
    '''
    Sort OCR-ed boxes into correct reading order

    Parameters
    ----------
        ocr_data: dict
            The OCR information of 1 image

    Returns
    -------
        ocr_data: dict
            Sorted OCR-ed boxes in the reading order
    '''
    word_size = 0

    size_list = [box['word_size'] for box in ocr_data['details'] if box['word_size'] != -1]
    boxes_word_size = sum_size = np.sum(size_list)
    count = 0
    valid_box_length = len(ocr_data['details']) - sum(1 for d in ocr_data['details'] if d.get('word_size') == -1)

    for box_index, box in enumerate(ocr_data['details']):
        if box['word_size'] == -1:
            continue
        average = (sum_size - box['word_size'])/(valid_box_length - 1)

        if box['word_size'] // average > 1 or average // box['word_size'] > 1:
            boxes_word_size -= box['word_size']
            count += 1

    word_size = boxes_word_size / (valid_box_length - count)
    ocr_data['details'] = sorted(
        ocr_data['details'],
        key=lambda box: (-int(round(box['mid'][0]) // round(word_size)), box['mid'][1])
    )

    return ocr_data

def combine_box(ocr_data):
    '''
    Combine the transcription of all box in to 1 list of Han-Nom words

    Parameters
    ----------
        ocr_data: dict
            The OCR information of 1 image

    Returns
    -------
        ocr_words_list: list
            Combined Han-Nom transcription from all boxes in a page (image)
    '''
    ocr_words_list = []
    for i, box in enumerate(ocr_data['details']):
        for word in box['transcription']:
            word_info = {'box_index': i,
                         'word': word}
            ocr_words_list.append(word_info)

    return ocr_words_list

def compareWord(ocr_char, origin_char, translation, similar):
    '''
    Compare between the ocr char and original char

    Parameters
    ----------
        ocr_char: chr
            OCR-ed words need to be compared
        origin_char: chr
            Origin word need to be compared (Quoc Ngu)
        translation: dict
            Dictionary of Quoc Ngu
        similar: dict
            Dictionary of similar Han-Nom words

    Returns
    -------
        0: Wrong OCR (word not exist in both dictionary)
        1: OCR right
        >1: OCR wrong (OCR similar words)
    '''

    # Get the translation list of Han-Nom words for the original Quoc Ngu (QN_Similar)
    HN_dic = []
    if quoc_ngu_word_normalize(origin_char) in translation:
        HN_dic = translation[quoc_ngu_word_normalize(origin_char)]

    # Check the OCR-ed with the translation list (QN_Similar)
    if ocr_char in HN_dic:
        # OCR almost correct
        return 1
    else:
        # Get the list of similar Han-Nom words (SN_Similar)
        if ocr_char in similar:
            similar_list = similar[ocr_char]

            # Use filter to get the intersection
            intersection = list(filter(lambda item: item in HN_dic, similar_list))
            if len(intersection) != 0:
                # OCR similar word (count as not equal in Levenshtein)
                return 2
        # OCR wrong
        return 0

def word_levenshtein(ocr_box, QN_sentence, translation, similar):
    '''
    Align the whole combined Han-Nom transcription with the all the Quoc Ngu in the corresponded image
    (Word-by-word alignment)
    Parameters
    ----------
        ocr_box: list
            The list of combine boxes transcription
        QN_sentence: list
            Word by word list of the whole Quoc Ngu page (image)
        translation: dict
            Dictionary of Quoc Ngu
        similar: dict
            Dictionary of similar Han-Nom words
    Returns
    -------
        score: int
            Score of Levenshtein algorithm
        alignment: list(tuples)
            List of tuple store the alignment (x, y, z):
                - x: the index of word in the OCR-ed page
                - y: the corresponded index of word in the Quoc Ngu page
                - z: the state between 2 word (deletion, insertion, substitution)
    '''
    len_ocr = len(ocr_box)
    len_QN = len(QN_sentence)

    # Initialize the DP matrix with dimensions (len_ocr+1)x(len_correct+1)
    dp = np.zeros((len_ocr + 1, len_QN + 1), dtype=int)

    # Initialize the first row and column
    dp[0, :] = np.arange(len_QN + 1)
    dp[:, 0] = np.arange(len_ocr + 1)
    backtrack_dp = dp.copy()
    comparison = dp.copy()

    # Fill the DP table
    for i in range(1, len_ocr + 1):
        for j in range(1, len_QN + 1):
            comparison[i, j] = compareWord(ocr_box[i - 1]['word'], QN_sentence[j - 1], translation, similar)
            cost = 0 if comparison[i, j] else 2
            diag = dp[i - 1, j - 1] + cost
            left = dp[i, j - 1] + 1
            down = dp[i - 1, j] + 1

            temp_list = [diag, left, down]
            dp[i, j] = min_val = min(temp_list)

            path = temp_list.index(min_val)
            backtrack_dp[i, j] = path

    # Backtrack to find alignment
    i, j = len_ocr, len_QN
    alignment = []

    while i > 0 or j > 0:
        if i > 0 and j > 0 and backtrack_dp[i, j] == 0:
            # No change
            alignment.append((i - 1, j - 1, comparison[i, j]))
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or backtrack_dp[i, j] == 1):
            alignment.append((-1, j - 1, 0))  # Insertion in Correct
            j -= 1
        elif i > 0 and (j == 0 or backtrack_dp[i, j] == 2):
            alignment.append((i - 1, -1, 0))  # Deletion in OCR
            i -= 1


    alignment.reverse()
    score = dp[len_ocr, len_QN]

    return score, alignment

def charAlignment(ocr_data, QN_word, sinoNom_list, translation, similar):
    '''
    Align the character for each OCR-ed box corresponded to the whole page word-by-word alignment

    Parameters
    ----------
        ocr_data: dict
            The list of information of OCR-ed boxes
        QN_word: list
            The word by word Quoc Ngu text of the whole page
        sinoNom_list: list
            The combined OCR transcription of the whole page
        translation: dict
            The dictionary of Quoc Ngu
        similar: dict
            The dictionary of similar Han-Nom
    Returns
    -------
        ocr_data: dict
            OCR-ed boxes after align and add more attribute to each box
    '''
    score, alignment = word_levenshtein(sinoNom_list, QN_word, translation, similar)
    current_align_index = 0
    for box_index, box in enumerate(ocr_data['details']):
        sinoNom_list_index = [i for i, item in enumerate(sinoNom_list) if item.get("box_index") == box_index]
        color = []
        while current_align_index < len(alignment):
            sino_index = alignment[current_align_index][0]
            quoc_ngu_index = alignment[current_align_index][1]
            align_type = alignment[current_align_index][2]

            pigment = (sino_index, quoc_ngu_index, align_type)
            if sino_index != -1:
                if sino_index in sinoNom_list_index:
                    sinoNom_list_index.remove(sino_index)
                else:
                    break
            current_align_index += 1
            color.append(pigment)

        ocr_data['details'][box_index]['color'] = color

    return ocr_data

def colorText(color_list, text, default, blue, red, mode='ocr'):
    '''
    Create a color string for Excel

    Parameters
    ----------
        color_list: list
            The list of color for each character in the text
        text: list
            The text needed to be formated
        default: dict
            The default format information
        blue: dict
            The blue format information
        red: dict
            The red format information
        mode: str
            The mode to color the OCR-ed Han-Nom or to color the original Quoc Ngu sentence
    Returns
    -------
        format_pairs: list
            List of character and their format
    '''
    format_pairs = []
    text_mode = 0

    if mode == 'ocr':
        text_mode = 0
    elif mode == 'origin':
        text_mode = 1

    for color in color_list:
        text_index = color[text_mode]

        if text_index == -1:
            format_pairs.extend((red, '-' if text_mode == 0 else '- '))
        else:
            if text_mode == 0:
                # Wrong OCR
                if color[2] == 0:
                    format_pairs.extend((red, text[text_index]['word']))
                # Right OCR
                elif color[2] == 1:
                    format_pairs.extend((default, text[text_index]['word']))
                # Similar OCR
                else:
                    format_pairs.extend((blue, text[text_index]['word']))
            else:
                # Wrong OCR
                if color[2] == 0:
                    format_pairs.extend((red, (text[text_index] + ' ') if text_index != len(text) - 1 else text[text_index]))
                # Right OCR
                elif color[2] == 1:
                    format_pairs.extend((default, (text[text_index] + ' ') if text_index != len(text) - 1 else text[text_index]))
                # Similar OCR
                else:
                    format_pairs.extend((blue, (text[text_index] + ' ') if text_index != len(text) - 1 else text[text_index]))
    return format_pairs

def writeExcel(translation_dic, similar_dic, output_name, han_nom_path, quoc_ngu_path):
    '''
    Create Excel file

    Parameters
    ----------
        translation_dic: dict
            The dictionary of Quoc Ngu
        similar_dic: dict
            The dictionary of similar Han-Nom
        output_name: str
            The output excel file name
        han_nom_path: str
            The path to the OCR-ed Han Nom json folder
        quoc_ngu_path: str
            The path to the Quoc Ngu text folder
    Returns
    -------
    '''


    '''
    ----------------
    SPECIFY THE NAME AND PATH ON OUTPUT EXCEL FILE
    ----------------    
    '''
    workbook = xlsx.Workbook(output_name + '.xlsx') # Adjust this name for the excel file


    # Font of default format
    default_format = workbook.add_format({
        'font_name': 'Nom Na Tong',
        'font_size': 14,
        'color': 'black'
    })

    # Font of red color
    red_format = workbook.add_format({
        'font_name': 'Nom Na Tong',
        'font_size': 14,
        'color': '#FF0000'
    })

    # Font of blue color
    blue_format = workbook.add_format({
        'font_name': 'Nom Na Tong',
        'font_size': 14,
        'color': '#0000FF'
    })

    # Font of green color
    green_format = workbook.add_format({
        'font_name': 'Nom Na Tong',
        'font_size': 14,
        'color': '#00FF00'
    })

    # Font of header
    head_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'font_name': 'Nom Na Tong',
        'font_size': 14
    })

    # Font of image ID
    arial_format = workbook.add_format({
        'font_name': 'Arial',
        'font_size': 11
    })

    # Write header for excel file
    worksheet = workbook.add_worksheet("Tu Chung Luoc Thuyet")
    columns = ["Image_name", "ID", "Image Box", "SinoNom OCR", "Chữ Quốc ngữ"]

    for col_num, header in enumerate(columns):
        worksheet.write(0, col_num, header, head_format)

    row_num = 1

    # List all files in the folder
    file_names = os.listdir(han_nom_path)

    # Filter out JSON files and remove the .json extension
    json_files = [os.path.splitext(file)[0] for file in file_names if file.endswith('.json')]

    for page in json_files:
        pdf_name, page_number = page.split('_page')
        image_file_path_ocr = f"{han_nom_path}\\{page}.json"
        quoc_ngu_text_path = f"{quoc_ngu_path}\\{page}"
        if not os.path.exists(image_file_path_ocr):
            continue
        ocr_data = ocr_json_read(image_file_path_ocr)
        QN_word, QN_text = extractText(quoc_ngu_text_path)

        ocr_data = boxSort(ocr_data)
        sinoNom_list = combine_box(ocr_data)
        ocr_data = charAlignment(ocr_data, QN_word, sinoNom_list, translation_dic, similar_dic)
        print(f"[+] Creating {page}...")
        box_index = 0
        for box in ocr_data['details']:
            extra_box_check = 1
            for qn_index in box['color']:
                if qn_index[1] != -1:
                    extra_box_check = 0
                    break
            if extra_box_check:
                continue

            # Write the Image name
            image_name = f"{page}.png"
            worksheet.write(row_num, 0, image_name, arial_format)

            # Get and write the Image ID format
            box_id = f"{pdf_name}.{page_number:03}.{box_index+1:03}"
            worksheet.write(row_num, 1, box_id, arial_format)
            box_index += 1

            # Change point coordinates into suitable format
            point_format = f'{[tuple(i) for i in box["points"]]}'

            # Check extra OCR box
            worksheet.write(row_num, 2, point_format, default_format)

            color = box['color']
            # Color the SinoNom OCR
            if len(color) == 1:
                sinoChar = {}
                quocNguChar = {}
                if color[0][0] == -1:
                    sinoChar = '-'
                else:
                    sinoChar = sinoNom_list[color[0][0]]
                if color[0][1] == -1:
                    quocNguChar = '-'
                else:
                    quocNguChar = QN_text[color[0][1]]

                if color[0][2] == 1:
                    worksheet.write(row_num, 3, sinoChar['word'], default_format)
                    worksheet.write(row_num, 4, quocNguChar, default_format)
                elif color[0][2] == 2:
                    worksheet.write(row_num, 3, sinoChar['word'], blue_format)
                    worksheet.write(row_num, 4, quocNguChar, blue_format)
                else:
                    worksheet.write(row_num, 3, sinoChar['word'], red_format)
                    worksheet.write(row_num, 4, quocNguChar, red_format)

            else:
                format_pairs = colorText(color, sinoNom_list, default_format, blue_format, red_format, 'ocr')
                worksheet.write_rich_string(row_num, 3, *format_pairs)

                # Color the Quoc Ngu
                format_pairs = colorText(color, QN_text, default_format, blue_format, red_format, 'origin')
                worksheet.write_rich_string(row_num, 4,  *format_pairs)

            row_num += 1

        print(f"[+] Done creating {page}")
    print(f"[+] Done writing Excel")
    workbook.close()

def main():
    # Path to similar SinoNom
    similar_file = "SinoNom_similar_Dic.xlsx"

    # Path to SinoNom-Quoc Ngu dictionary
    translation_file = "QuocNgu_SinoNom_Dic.xlsx"

    similar_dic = similarRead(similar_file)
    translation_dic = translationRead(translation_file)

    # The output excel file name
    output_name = "Sách Nôm công giáo 1995 - 100 - Tu Chung Luoc Thuyet"

    # Path to Han-Nom ocr result folder (json)
    han_nom_ocr_path = "Han-Nom_ocr"

    # Path to Quoc Ngu text folder
    quoc_ngu_text_path = "Quoc-Ngu_text"

    writeExcel(translation_dic, similar_dic, output_name, han_nom_ocr_path, quoc_ngu_text_path)


if __name__ == "__main__":
    main()