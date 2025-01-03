import numpy as np
import os
import json
import pandas as pd
from functools import cmp_to_key
import re
from xlsxwriter.workbook import Workbook

#############################################################

QUOCNGU_SINONOM_PATH = r"D:\NLP_Project\data_prepare\NLP_Project_Group6\QuocNgu_SinoNom_Dic.xlsx"

#############################################################

QN_File_Path = r"output//vietnamese_label//annotations_cleaned.json"
QN2_File_Path = r"output//vietnamese_label//annotations_3_cleaned.json"
HN_Folder_Path = r"output//OCR_Cleaned_HN//"
HN_File_Name = r"ocr_Cleaned_"
HN2_File_Name = r"ocr_3_Cleaned_"

output_filename = "Khanh_TCQN_HN"
output_filename_2 = "Khanh_TNYL_P2_HN"
output_excel = "output2.xlsx"


#############################################################


quocngu_sinonoms_df = pd.read_excel(QUOCNGU_SINONOM_PATH)
ignored_page = [49, 60]
##############################################################
# folder does't contain this page


def Vietnamese_Page_Setup(FilePath):
    with open(FilePath, "r", encoding="utf-8") as file:
        data = json.load(file)

    new_data = []
    for filename, text in data.items():
        text = re.sub(r'[^a-zA-ZÀ-ỹ\s]', '', text)  

        words = text.split()
        text = ' '.join(words)
        # print(text)
        # print("==================================")
        new_data.append(text)
    
    return new_data

def HN_Page_Setup(FolderPath, image_name, start, end):
    datas = []

    for index in range(start + 1, end + 1):
        if(index in ignored_page):
            datas.append(0)
            continue
        with open(os.path.join(FolderPath, image_name + str(index) + ".json"), "r", encoding="utf-8") as file:
            data = json.load(file)
        datas.append(data)
    return datas

###################################################################################
def get_sinonoms_for_word(df, word):
    df.columns = ['QuocNgu', 'SinoNom']
    return df[df['QuocNgu'] == word]['SinoNom'].tolist()
###############################################################################
def minimum_edit_distance(A, B):
    # m, n = len(A), len(B)
    # dp = [[0] * (n + 1) for _ in range(m + 1)]

    # for i in range(m + 1):
    #     dp[i][0] = i  
    # for j in range(n + 1):
    #     dp[0][j] = j  

    # # Điền bảng dp
    # for i in range(1, m + 1):
    #     for j in range(1, n + 1):
    #         if A[i - 1] in get_sinonoms_for_word(quocngu_sinonoms_df, B[j - 1]):
    #             dp[i][j] = dp[i - 1][j - 1]
    #         else:
    #             dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    # return dp[m][n]

    distance = 0
    for index in range(0, len(A)):
        if(index >= len(B)):
            distance += 1
            continue
        if(A[index] not in get_sinonoms_for_word(quocngu_sinonoms_df, B[index].lower())):
            distance += 1
    
    return distance


def Align_Box_In_Page(hn_page, qn_page, filename, page_number):
    """
        Input : 
            hn_page : dictionary :
                + "image_name" -> name of page
                + "OCR_Result" -> list of box(dictionary):
                    + "transcription" -> box ocr_result
                    + "points" -> points of box
            qn_page : string
        Output : 
            List of (filename, box, qn, points)
    """
    qn_words = qn_page.split(' ')
    start_index = 0

    boxes = []
    for index in range(0, len(hn_page['OCR_Result'])):
        data = {}
        data['ID'] = filename + "." + str(page_number + 1).zfill(3) + "." + str(index + 1).zfill(3)
        data['points'] = hn_page['OCR_Result'][index]['points'] if len(hn_page['OCR_Result'][index]['points']) != 2 else hn_page['OCR_Result'][index]['points'][0]
        data['SinoNomOCR'] =  hn_page['OCR_Result'][index]['transcription']
        data['image_name'] = filename + "_page" + str(page_number + 1).zfill(3) + ".png"
        data['QN'] = ""
        data['color_box'] = True

        if(start_index >= len(qn_words)):
            continue

        length = len(hn_page['OCR_Result'][index]['transcription'])
        flag = False
        listOfSupString = []
        for supstring_index in range(0, 7):
            is_break = False
            if(start_index + supstring_index + length < len(qn_words)):
                sup_string = qn_words[start_index + supstring_index: start_index + supstring_index + length ]
            else:
                sup_string = qn_words[start_index + supstring_index: len(qn_words)]
                is_break = True

            Med = minimum_edit_distance(hn_page['OCR_Result'][index]['transcription'], sup_string)
            LengthOfWord = len(sup_string)
            # qn_sentence = ' '.join(sup_string)
            if(Med <= 5 and length > Med + 1):
                data['QN'] = ' '.join(sup_string)
                if(length == len(sup_string)):
                    data['color_box'] = False
                flag = True
                start_index += LengthOfWord + supstring_index
                break
            else:
                listOfSupString.append((sup_string, Med, LengthOfWord + supstring_index))
            
            if(is_break):
                break
        
        if(flag == False and listOfSupString):
            min_tuple = min(listOfSupString, key=lambda x: x[1])
            data['QN'] = ' '.join(min_tuple[0])
            if(len(min_tuple[0]) == length):
                data['color_box'] = False
            start_index += min_tuple[2]
        boxes.append(data)
    
    return boxes

def Align_Box(QN_Pages, HN_Pages, filename, start, end):
    result = []
    for index in range(start, end):
        if(index == 48 or index == 59):
            continue
        data = Align_Box_In_Page(HN_Pages[index], QN_Pages[index], filename, index)
        result += data
        print("done" + str(index))

    return result

def align_Word_Pages(HN_Sentences, QN_Sentences):
    color_words = []      
    QN_words = QN_Sentences.split()
    for index in range(0, len(HN_Sentences)):
        if(index >= len(QN_words)):
            color_words.append(1)
            continue
        if(HN_Sentences[index] in get_sinonoms_for_word(quocngu_sinonoms_df, QN_words[index])):
            color_words.append(0)
        else:
            color_words.append(1)
        
    return color_words

def align_Word(QN_HN_pages):
    result = []
    for item in QN_HN_pages:
        item['color_word'] = align_Word_Pages(item['SinoNomOCR'], item['QN'].lower())
        result.append(item)
    
    return result

def write_to_excel(QN_HN_Pages, output_file):
    data = {
        'Image_name': [temp['image_name'] for temp in QN_HN_Pages],
        'ID': [temp['ID'] for temp in QN_HN_Pages],
        'Image Box': [temp['points'] for temp in QN_HN_Pages],
        'SinoNom OCR': [temp['SinoNomOCR'] for temp in QN_HN_Pages],
        'Chữ Quốc ngữ': [temp['QN'] for temp in QN_HN_Pages],
    }
    QN_HN_Pages = align_Word(QN_HN_Pages)

    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook, worksheet = writer.book, writer.sheets['Sheet1']
    format_green, format_red, format_blue = workbook.add_format({'color': 'green'}), workbook.add_format({'color': 'red'}), workbook.add_format({'color': 'blue'})

    for row_num in range(len(df)):
        worksheet.write(row_num + 1, 2, str(df.iloc[row_num, 2]), format_green if QN_HN_Pages[row_num]['color_box'] else None)
        
        formatted_ocr = []
        for index in range(len(QN_HN_Pages[row_num]['SinoNomOCR'])):
            if QN_HN_Pages[row_num]['color_word'][index] == 1:
                formatted_ocr.extend([format_red, QN_HN_Pages[row_num]['SinoNomOCR'][index]])
            else:
                formatted_ocr.append(QN_HN_Pages[row_num]['SinoNomOCR'][index])
        worksheet.write_rich_string(row_num + 1, 3, *formatted_ocr)

        for col_num in range(len(df.columns)):
            if col_num != 2 and col_num != 3:
                worksheet.write(row_num + 1, col_num, str(df.iloc[row_num, col_num]))

    writer.close()
    print(f"Đã ghi dữ liệu vào '{output_file}' thành công.")



# QN_Pages_1 = Vietnamese_Page_Setup(QN_File_Path)
# HN_Pages_1 = HN_Page_Setup(HN_Folder_Path, HN_File_Name, start=0, end=166)

# QN_HN_pages_1 = Align_Box(QN_Pages_1, HN_Pages_1, output_filename,start=0, end=166)


QN_Pages_2 = Vietnamese_Page_Setup(QN2_File_Path)
HN_Pages_2 = HN_Page_Setup(HN_Folder_Path, HN2_File_Name, start=0, end=22)

QN_HN_pages_2 = Align_Box(QN_Pages_2, HN_Pages_2, output_filename_2, start=0, end=22)
 

QN_HN_pages =   QN_HN_pages_2
write_to_excel(QN_HN_pages, "output2.xlsx")

