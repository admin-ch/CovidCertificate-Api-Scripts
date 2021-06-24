import re

from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from base64 import encodebytes
from base64 import b64decode

def getOTP():
    """Get the onetime password from the otp.txt file

    Returns:
        The one time password stored in otp.txt
    """
    f = open('otp.txt', )
    otp = f.read()
    f.close()
    return otp

normalizedReplaceRegex = re.compile(r"[\n\r\t ]")

def sign(payload, certificate, passphrase):
    """Sign the content of the payload with the PKI certificate

    Args:
        payload: the payload to be signed
        certificate: the PKI certificate name used to make the signature, without extension
        password: Password for the PKI private key certificate
    Returns:
        signature: the signature of the payload, signed with the PKI certificate
    """
    # private_key = RSA.import_key(open(certificate+".key").read())
    private_key = RSA.importKey(open(certificate+".encrypted.key", "rb").read(), passphrase=passphrase)
    signer = PKCS1_v1_5.new(private_key)
    normalized_payload = re.sub(normalizedReplaceRegex, "", payload)
    signature = signer.sign(SHA256.new(normalized_payload.encode('utf-8')))
    return encodebytes(signature).decode().replace("\n", "")

def createCurl(payload, signature, certificate, certificateType, verbosity, password, staging):
    """Create a curl request based on the template curl_template.txt in which the payload, the signature, the PKI certificate and the verbosity is injected

    Args:
        payload: the payload for creating a covid certificate
        signature: the signature of the payload
        certificate: the PKI certificate name used to create the TLS tunnel, without extension
        certificateType: the type of covid certificate that needs to be produced. It can be "vaccination", "test" or "recovery".
        verbosity: make the curl non silent if true
        password: Password for the PKI private key certificate
        staging: Staging environment used for managing the requests. It can be PROD or ABN

    Returns:
        curl: the curl request
    """
    escapedPayload = payload.replace("'","\'\"\'\"\'")
    f = open('curl_template.txt', )
    curl = f.read()
    curl = curl.replace("SIGNATURE_PLACEHOLDER", signature)
    curl = curl.replace("PAYLOAD_PLACEHOLDER", escapedPayload)
    curl = curl.replace("CERTIFICATE_PLACEHOLDER", certificate)
    curl = curl.replace("CERTIFICATETYPE_PLACEHOLDER", certificateType)
    curl = curl.replace("PASSWORD_PLACEHOLDER", password)
    if verbosity:
        curl = curl.replace("SILENT_PLACEHOLDER", "")
    else:
        curl = curl.replace("SILENT_PLACEHOLDER", "--silent")
    if staging == 'PROD':
        curl = curl.replace("API_PLACEHOLDER", "ws.covidcertificate.bag.admin.ch")
    else:
        curl = curl.replace("API_PLACEHOLDER", "ws.covidcertificate-a.bag.admin.ch")

    return curl

def createPDF(pdf, uvci, store):
    """Create a pdf with the result of the curl request

    Args:
        pdf: the pdf data sent back
        uvci: the uvci sent back - UVCI is the unique identifier of the covid certificate
        store: store the pdf file.

    Returns:
        pdf_filename: the name of the created pdf

        """
    pdf_filename = uvci + ".pdf"
    if store:
        f = open(pdf_filename, "wb")
        f.write(b64decode(pdf, validate=True))
        f.close()
    return pdf_filename