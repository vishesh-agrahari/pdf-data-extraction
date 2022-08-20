import json
import cv2
from pdf2image import convert_from_path
from pyzbar import pyzbar
import jwt
# extract qr code data from pdf
def extractQrCodeData(n):
    jsonArray = {}
    for i in range(n):
        # read images using opencv
        img = cv2.imread('pdf2image\\page' + str(i) + '.jpg')
        barcodes = pyzbar.decode(img)
        bdata = barcodes[0].data.decode()
        jsonArray['page'+str(i)] = jwt.decode(bdata, options={"verify_signature": False})
    return jsonArray

# convert csv file to json
def write_to_json(jsonArray, jsonFilePath, mode):
     # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, mode, encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)

# converting pdf to image
def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path, poppler_path=r"C:\Users\visheshAgrahari\Downloads\poppler-0.68.0\bin")
    for i in range(len(images)):
        # Save pages as images
        images[i].save('pdf2image\\page' + str(i) + '.jpg', 'JPEG')
    return len(images)

if __name__ == '__main__':
    # input pdf file location
    pdfPath = input("enter path of pdf file: ")
    # # convert all pages of pdf into images
    n = convert_pdf_to_image(pdfPath)
    # extract QRCode data
    qrCodeData = extractQrCodeData(n)
    # write json data in output file
    write_to_json(qrCodeData, 'output\\JsonData.json', 'w')
    print(qrCodeData)
