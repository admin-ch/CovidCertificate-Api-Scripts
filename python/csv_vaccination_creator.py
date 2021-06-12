# Module containing global functions necessary to script covid certificate creation with curl
import csv
import timeit
import os
import json
import argparse
import glob

import pandas as pd
from datetime import datetime

import covidcertificate as cc

# Start timer
start = timeit.default_timer()

def createPayload(otp, csv_row):
    """Create the payload based on vaccination.json or vaccination_print.json, in which the one time password and the data (one row) are injected

        Args:
            otp: the one time password
            csv_row: one row of the csv file
        Returns:
            payload: the payload of the covid certificate
    """
    # Selection of payload muster: 2 options: normal or print
    if ('zipCode' in csv_row and 'city' in csv_row):
        f = open('vaccination_print.json', )
    else:
        f = open('vaccination.json', )
    raw_dict = json.load(f)
    raw_dict['otp'] = otp
    raw_dict['name']['familyName'] = csv_row['familyName']
    raw_dict['name']['givenName'] = csv_row['givenName']
    raw_dict['dateOfBirth'] = csv_row['dateOfBirth']
    raw_dict['language'] = csv_row['language']
    raw_dict['vaccinationInfo'][0]['medicinalProductCode'] = csv_row['medicinalProductCode']
    raw_dict['vaccinationInfo'][0]['numberOfDoses'] = csv_row['numberOfDoses']
    raw_dict['vaccinationInfo'][0]['totalNumberOfDoses'] = csv_row['totalNumberOfDoses']
    raw_dict['vaccinationInfo'][0]['vaccinationDate'] = csv_row['vaccinationDate']
    raw_dict['vaccinationInfo'][0]['countryOfVaccination'] = csv_row['countryOfVaccination']
    if ('zipCode' in csv_row and 'city' in csv_row):
        raw_dict['address']['streetAndNr'] = csv_row['streetAndNr']
        raw_dict['address']['zipCode'] = csv_row['zipCode']
        raw_dict['address']['city'] = csv_row['city']
        raw_dict['address']['cantonCodeSender'] = csv_row['cantonCodeSender']
    raw_string = json.dumps(raw_dict)
    f.close()
    payload = ''.join(raw_string.split())
    return payload

def main():
    """main script function with argument management

    """
    # Parse input arguments
    parser = argparse.ArgumentParser(description='This tool allows you to make mass generation of vaccination covid certificates.')
    parser.add_argument('--filename', dest='filename', type=str, default="vaccination.csv", help='Name of the input csv file. Per default: vaccination.csv')
    parser.add_argument('--pkicertificate', dest='pkicertificate', type=str, default="ZH-spital-A-t.bit.admin.ch",
                        help='Name of the PKI certificate, without extension Per default: ZH-spital-A-t.bit.admin.ch')
    parser.add_argument('--password', dest='password', type=str,
                        help='Password for the PKI private key certificate')
    parser.add_argument('--staging', dest='staging', type=str, default="ABN",
                        help='Staging environment used to send the requests. Per default: ABN. It can be PROD (production environment) or ABN (test environment)')
    parser.add_argument("-clean", help="Delete certificates pdf, logger and retry files", default=False, action="store_true")
    parser.add_argument("-verbose", help="Increase output verbosity", default=False, action="store_true")
    parser.add_argument("-progress", help="Inform about certificate creation progress", default=False, action="store_true")
    args = parser.parse_args()

    if (args.clean):
        pdfList = glob.glob("urn:uvci:01:CH*.pdf")
        for file in pdfList:
            os.remove(file)
        loggerList = glob.glob("Logger*.csv")
        for file in loggerList:
            os.remove(file)
        retryList = glob.glob("Retry*.csv")
        for file in retryList:
            os.remove(file)
        exit()

    # Read the one time password
    otp = cc.getOTP()

    # Get the data of recovery csv file
    recoveryData = pd.read_csv(args.filename,sep=';',header='infer')

    # Create a logger to store the result of the file creation and a retry for covid certificates that couldn't be created
    fileTimestamp = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    logger = open("Logger_"+fileTimestamp+"_recovery.csv", "w")
    retry = open("Retry_"+fileTimestamp+"_recovery.csv", "w")
    writer_retry = csv.writer(retry)
    writer_retry.writerow(recoveryData.columns)
    counter = 0

    for index, row in recoveryData.iterrows():
        # Create the payload
        payload = createPayload(otp, row)
        # Get the payload and its signature
        signature = cc.sign(payload, args.pkicertificate, args.password)
        # Create a curl request based on the payload
        curlRequest = cc.createCurl(payload, signature, args.pkicertificate, "vaccination", args.verbose, args.password, args.staging)
        # Execute the curl request
        output = os.popen(curlRequest)

        try:
            # Get the json from the curl response and extract the pdf and uvci content
            response = json.load(output)
            pdf = response['pdf']
            uvci = response['uvci']
            # Create pdf with the response information
            logger.write(str(index) +";OK;"+cc.createPDF(pdf, uvci)+"\n")
            counter = counter + 1
            if (args.progress):
                print(str(counter) + " certificate(s) created: " + uvci + ".pdf")
        except:
            logger.write(str(index) + ";ERROR;\n")
            writer_retry.writerow(row)
            if (args.progress):
                print("Certificate creation error - see retry file")

    stop = timeit.default_timer()

    logger.write("#certificates created:;"+ str(counter) + ";\n")
    logger.write("Duration:;"+ str("{:.2f}".format((stop - start))) + ";\n")
    logger.write("Certificates/s:;"+ (str("{:.2f}".format((counter/(stop - start))))) + ";\n")

    logger.close()
    retry.close()

main()