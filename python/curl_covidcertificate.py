import os
import json
import argparse
import glob

import covidcertificate as cc

def createPayload(otp, certificatetype):
    """Create the payload based on the vaccination_muster.json file, in which the one time password is injected

        Args:
            otp: the one time password
            certificatetype: type of certificate to be produced
        Returns:
            payload: the payload of the covid certificate
    """
    f = open(certificatetype+"_muster.json", )
    raw_dict = json.load(f)
    raw_dict['otp'] = otp
    raw_string = json.dumps(raw_dict)
    f.close()
    return raw_string

def main():
    """main script function with argument management

    """
    # Parse input arguments
    parser = argparse.ArgumentParser(description='This tool allows you to one covid certificate.')
    parser.add_argument('--certificatetype', dest='certificatetype', type=str, default="vaccination", help='Certificate type to be produced: vaccination, test or recovery.')
    parser.add_argument('--pkicertificate', dest='pkicertificate', type=str, default="ZH-spital-A-t.bit.admin.ch",
                        help='Name of the PKI certificate, without extension Per default: ZH-spital-A-t.bit.admin.ch')
    parser.add_argument('--staging', dest='staging', type=str, default="ABN",
                        help='Staging environment used to send the requests. Per default: ABN. It can be PROD (production environment) or ABN (test environment)')
    parser.add_argument('--password', dest='password', type=str,
                        help='Password for the PKI private key certificate')
    parser.add_argument("-clean", help="Delete certificates pdf", default=False, action="store_true")
    parser.add_argument("-verbose", help="Increase output verbosity", default=False, action="store_true")
    args = parser.parse_args()

    if (args.clean):
        pdfList = glob.glob("urn:uvci:01:CH*.pdf")
        for file in pdfList:
            os.remove(file)
        exit()

    # Read the one time password
    otp = cc.getOTP()

    # Create payload
    payload = createPayload(otp, args.certificatetype)
    # Get the payload and its signature
    signature = cc.sign(payload, args.pkicertificate, args.password)
    # Create a curl request based on the payload
    curlRequest = cc.createCurl(payload, signature, args.pkicertificate, args.certificatetype, args.verbose, args.password, args.staging)
    if (args.verbose):
        print("Curl request:")
        print(curlRequest)
    # Execute the curl request
    output = os.popen(curlRequest)

    try:
        # Get the json from the curl response and extract the pdf and uvci content
        response = json.load(output)
        pdf = response['pdf']
        uvci = response['uvci']
        # Create pdf with the response information
        pdf = cc.createPDF(pdf, uvci)
        if(args.verbose):
            print("Certificate " + pdf + " created.")
    except:
        if (args.verbose):
            print("Error with certificate creation")

main()