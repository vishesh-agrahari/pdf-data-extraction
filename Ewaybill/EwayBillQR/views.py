import os
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render
from pyrsistent import immutable
from pyzbar import pyzbar
import cv2
import re
import json
import pandas as pd
from pdf2image import convert_from_path
import time
from django.views.decorators.csrf import csrf_exempt
from jproperties import Properties
from .models import qrdata

# extract qr code data from pdf
def extractQrCodeData(n):
    qrCodeData = []
    for i in range(n):
        # read images using opencv
        img = cv2.imread('pdf2image\\page' + str(i) + '.jpg')
        barcodes = pyzbar.decode(img)
        bdata = barcodes[0].data.decode()
        qrCodeData.append(bdata)
    return qrCodeData

# convert string to list - qrcode data
def convert_to_List(string):
    li = list(string.split(" "))
    if(re.search("^[a-zA-Z]", li[1]) != None):
        for k in range(2,len(li)-1):
            li[1]= li[1]+ ' '+ li[k]
        while(len(li)!=3):
            li.pop(2)
    else:
        li[1] = li[1] + ' ' + li[2] + li[3]
        li[4] = li[4] + ' ' + li[5] + li[6]
        li.pop(2)
        li.pop(2)
        li.pop(3)
        li.pop(3) 
    return li

# insert values to database
def add_To_DB(dict_data):
     ewbno=  dict_data.get('EwbNo')
     ewbdate = dict_data.get('EwbDt ')
     gendate = dict_data.get('Gen Dt')
     ewbvalidtill=  dict_data.get('EwbValidTill')
     genby = dict_data.get('Gen By')
     reg = qrdata(ewb_no=ewbno,ewb_date=ewbdate,gen_date=gendate,ewb_valid_till=ewbvalidtill,gen_by=genby)
     reg.save()


# extract field and row values for qrcode data
def fields_And_Values_Qrcodedata(Qrcode_data):
    jsonArray ={}
    jsonArray["status code"] = "200"
    jsonArray["message"]= "request successful"
    jsonArray["QRcode Data"]=[]
    configs = Properties()
    # extract column values from properties file
    with open('EwayBillQR\\eway-config.properties', 'rb') as config_file:
            configs.load(config_file)
    items_view = configs.items()
    header = []
    for item in items_view:
            header.append(item[1].data)
    # list of regular exp. to remove
    Reglist = ['EwbNo :-','EWB No.:', 'EwbDt : -','Gen. Dt.:', 'EwbValidTill :-', 'Gen By:-','Gen. By:']
    for d in Qrcode_data:
        for rg in Reglist:
            d = d.replace(rg, ' ')
        res = " ".join(d.split())
        res_list = convert_to_List(res)
        if(len(res_list)==3):
            res_list.insert(1,' ')
            res_list.insert(3,' ')
        else:
            res_list.insert(2,' ')
        row = dict(zip(header, res_list))
        add_To_DB(row)
        jsonArray["QRcode Data"].append(row)
    return JsonResponse(jsonArray)
    


@csrf_exempt
def scanQRCode(request):
    print("started...")
    """
    if(request.method=='POST'):
        try:
            file = request.FILES["file"]
            ext = os.path.splitext(file.name)[1] 
            if (ext.lower() != ".pdf"):
                return JsonResponse({'status code': '502','message':'Unsupported file extension.'})
        except:
            return JsonResponse({'status code': '501','message':'file not found'})
        # try:
        #     file_type = request.POST['filetype']
        #     if (file_type.lower() not in ["ewb","inv"]):
        #         return JsonResponse({'status code': '504','message':'file type is not appropriate'})
        # except:
        #     return JsonResponse({'status code': '503','message':'file type not found'})
        # write input file to local disc
        with open("input\\temp.pdf", 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # input pdf file location
        pdfPath = "input\\temp.pdf"
    """
    # assign directory
    directory = 'input\\Print Output'
    # iterate over files in that directory
    c=0
    for filename in os.scandir(directory):
        if filename.is_file():
            # convert all pages of pdf into images
            images = convert_from_path(filename.path, poppler_path="poppler-0.68.0\\bin")
            for i in range(len(images)):
                # Save pages as images
                images[i].save('pdf2image\\page' + str(c) + '.jpg', 'JPEG')
                print('pdf2image\\page' + str(c) + '.jpg created')
                c+=1
    try:
        # extract QRCode data
        qrCodeData = extractQrCodeData(c)
    except:
        return JsonResponse({'status code': '505','message':'Qrcode/Barcode is missing'})

    # spilit fields and values from qrcodedata and add to database
    return fields_And_Values_Qrcodedata(qrCodeData)
        
def getAll(request):
        data = list(qrdata.objects.values())  
        return JsonResponse(data, safe=False)

@csrf_exempt
def delAll(request):
        data = qrdata.objects.all().delete() 
        return JsonResponse({'status code': '200','message':'all data removed'})


    
    

