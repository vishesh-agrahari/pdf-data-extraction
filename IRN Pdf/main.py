from PIL import Image
import pytesseract
import csv
import json
import pandas as pd
import tabula
from pdf2image import convert_from_path
from pyzbar import pyzbar
import jwt
import time

# extract data from qrcode
def extractQrCodeData(img):
    barcodes = pyzbar.decode(img)
    bdata = barcodes[0].data.decode()
    print(jwt.decode(bdata,options={"verify_signature": False}))

# extract fields from pdf
def extract_keys():
    keys = ['Page no','Invoice No', 'Date', 'Doc Type', 'POS', 'Customer GSTIN ', 'Customer PAN',
            'Supply Type', 'Tax Scheme', 'Purchase Order No:', 'Purchase Order Date:', 'Reverse Charge', 'IRN',
            'AckNo','Ack Date','E-way Bill No:','Date:','Valid Till:','Bill From:','Bill_to','Ship_to','Product details','Total Invoice Amt (INR)']
    return keys

# extract values from pdf
def extract_values(keys,n):
    values =[]
    for i in range(n):
        image = 'pdf2image\\page' + str(i) + '.jpg'
        text = pytesseract.image_to_string(Image.open(image), lang="eng")
        text1 = text[text.find('Invoice No'):text.find('Bill From:')]

        value = []
        for j in range(len(keys) - 4):
            start = text1.find(keys[j]) + len(keys[j])
            end = text1.find(keys[j + 1])
            t = text1[start:end].replace("\n", "")
            if(j==11):
                t = t.replace('No —','')
            value.append(t)
        text2 = text[text.find('E-way Bill No:'):text.find('Bill From:')]
        if(len(text2)!=0):
            for k in range(len(keys)-4,len(keys)-1):
                start = text2.find(keys[k]) + len(keys[k])
                end = text2.find(keys[k + 1])
                t = text2[start:end].replace("\n", "")
                value.append(t)
        else:
            value.append('-')
            value.append('-')
            value.append('-')
        # extract values of bill_to,bill_from and ship_to
        with open("temptablecsv\\temp_csv" + str(i) + ".csv", 'r') as csvfile:
            Bill_to = ''
            Bill_from = ''
            Ship_to = ''
            # creating a csv reader object
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for t in csvreader:
                Bill_from += t[0]
                Bill_to = Bill_to + t[1] + t[2]
                Ship_to = Ship_to + t[3]
                if (len(t) > 4):
                    Ship_to += t[4]
                if (t[0].startswith('Contact:')):
                    break

            value.append(Bill_from)
            value.append(Bill_to)
            value.append(Ship_to)
            csvfile.close()
        value.append(text[text.find('Sr.'):text.find('Payee Information')].replace('\n',''))
        # append total invoice amount
        value.append(text[text.find('Total Invoice Amt (INR)')+len('Total Invoice Amt (INR)'):text.find('Total Invoice FC Amt')].split('\n')[0])
        # value.append(extractQrCodeData(image))
        value.insert(0,i+1)
        values.append(value)
    return values

# write data to csv file
def write_to_csv(keys, values, filePath):
    # write keys in csv file
    with open(filePath, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(keys)
    # writing the values into the file
    with open(filePath, 'a+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(values)

# convert csv file to json
def write_to_json(csvFilePath, jsonFilePath, mode, datafrom):
    # read csv file
    jsonArray = {}
    with open(csvFilePath, encoding='utf-8') as csvf:
        # load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf)
        jsonArray[datafrom] = []
        # convert each csv row into python dict
        for row in csvReader:
            # add this python dict to json array
            jsonArray[datafrom].append(row)

    # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, mode, encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


# convert csvfile to excel
def write_to_excel(csvFilePath, excelFilePath, sheetname, mode):
    # reading the csv file to dataframe
    df = pd.read_csv(csvFilePath)

    # converting the .csv file to .xlsx file
    with pd.ExcelWriter(excelFilePath, mode=mode) as writer:
        df.to_excel(writer, index=False, sheet_name=sheetname)


# convert table into temporary csv file
def convertTableIntoCsv(pdfPath,n):
    for i in range(n):
       tabula.convert_into(pdfPath, "temptablecsv\\temp_csv" + str(i) + ".csv", output_format="csv", pages=i+1)

# converting pdf to image
def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path, poppler_path=r"C:\Users\visheshAgrahari\Downloads\poppler-0.68.0\bin")
    for i in range(len(images)):
        # Save pages as images
        images[i].save('pdf2image\\page' + str(i) + '.jpg', 'JPEG')
    return len(images)

if __name__ == "__main__":
    # set path for pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\visheshAgrahari\AppData\Local\Tesseract-OCR\tesseract.exe'
    # input file location
    input_file = 'input\\ujjwalirn.pdf'
    n = convert_pdf_to_image(input_file)
    convertTableIntoCsv(input_file,n)
    keys = extract_keys()
    values = extract_values(keys[1:len(keys)-4],n)
    write_to_csv(keys, values, 'output\\TextCsvData.csv')
    write_to_json('output\\TextCsvData.csv', 'output\\JsonData.json', 'w', 'Invoice_Details')
    # write_to_excel('output\\TextCsvData.csv', 'output\\ExcelData.xlsx', 'TextDetails', 'w')