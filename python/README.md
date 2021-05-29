# Python scripts to use the Swiss Covid Certificate API

These scripts allow you to generate covid certificates. The scripts are provided as-is and we are very happy to receive feedbacks targeting to improve them.

They have been tested on macOS Big Sur with python 3.9.1. It was created for testing and demo purposes only. 

# Howto execute a curl for using the swiss covid certificate API ?

This HOWTO describes the usage of python code in order to use a curl request for testing the [swiss covid certificate API](https://github.com/admin-ch/CovidCertificate-Apidoc)

## Prerequisites
1. You have an access to Web management UI ([prod](https://www.covidcertificate.admin.ch/) - [test](https://www.covidcertificate-a.admin.ch/))
2. You have received a PKI certificate (.cer and .key files) of the type ["SwissGov Regular CA 01"](https://www.bit.admin.ch/bit/en/home/subsites/allgemeines-zur-swiss-government-pki/rootzertifikate/swiss-government-root-ca-ii.html)
3. Necessary python libraries are installed (for python 3):
```
pip3 install pycryptodomex
```
4. The PKI certificates are stored in the running directory.

## Procedure
1. Obtain a one time password from Web management UI ([prod](https://www.covidcertificate.admin.ch/) - [test](https://www.covidcertificate-a.admin.ch/))
2. Store the one time password in file otp.txt
3. Define covid certificate data in file muster file (vaccination_muster.json, test_muster.json or recovery_muster.json)
4. Run the script in your console (adapt the pkicertificate name and the password of the PKI certificate)
```
python3 curl_covidcertificate.py --certificatetype vaccination --pkicertificate ZH-spital-A-t.bit.admin.ch --password PASSWORD_TOREPLACE -verbose
```

# Howto script the generation of recovery certificates based on a csv file?

## Prerequisites
1. You have an access to Web management UI ([prod](https://www.covidcertificate.admin.ch/) - [test](https://www.covidcertificate-a.admin.ch/))
2. You have received a PKI certificate (.cer and .key files) of the type ["SwissGov Regular CA 01"](https://www.bit.admin.ch/bit/en/home/subsites/allgemeines-zur-swiss-government-pki/rootzertifikate/swiss-government-root-ca-ii.html) and you have the password of private key of this certificate
3. Necessary python libraries are installed (for python 3):
```
pip3 install pycryptodomex
```
## Procedure
1. Obtain a one time password from Web management UI ([prod](https://www.covidcertificate.admin.ch/) - [test](https://www.covidcertificate-a.admin.ch/))
2. Store the one time password in file otp.txt
3. Create a csv file equivalent to the recovery.csv file
5. Run the csv_recovery_creator.py file. It will create the certificates and make a log of work done and a retry file for not generated certificates. Adapt the password of the PKI certificate.
```
# For getting help:
python3 csv_recovery_creator.py --help
# Default usage:
python3 csv_recovery_creator.py --password PASSWORD_TOREPLACE
```

# Files and scripts in this directory

## Python scripts
- covidcertificate.py: module containing help functions used in order to manage the API requests 
- curl_covidcertificate.py: script to generate one single covid certificate based on data in a muster json file
- csv_recovery_creator.py: script to generate recovery covid certificates based on a csv file

## Templates
- curl_template.txt: template of curl request in which conten is injected by the python scripts
- test_muster.json: payload muster for test covid certificate
- vaccination_muster.json: payload muster for vaccination covid certificate
- recovery_muster.json: payload muster for recovery covid certificate
- recovery.json: payload template used to inject recovery data

## Data
- otp.txt: file containing the one time password necessary to access the API
- recovery.csv: csv file with data for a recovery covid certificate
- recovery.xlsx: excel file with data for a recovery covid certificate - can be used to produce a csv file
