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

def sign(payload, certificate):
    """Sign the content of the payload with the PKI certificate

    Args:
        payload: the payload to be signed
        certificate: the PKI certificate name used to make the signature, without extension
    Returns:
        signature: the signature of the payload, signed with the PKI certificate
    """
    private_key = RSA.import_key(open(certificate+".key").read())
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(SHA256.new(payload.encode('utf-8')))
    return encodebytes(signature).decode().replace("\n", "")

def createCurl(payload, signature, certificate, certificateType, verbosity, password):
    """Create a curl request based on the template curl_template.txt in which the payload, the signature, the PKI certificate and the verbosity is injected

    Args:
        payload: the payload for creating a covid certificate
        signature: the signature of the payload
        certificate: the PKI certificate name used to create the TLS tunnel, without extension
        certificateType: the type of covid certificate that needs to be produced. It can be "vaccination", "test" or "recovery".
        verbosity: make the curl non silent if true
        password: Password for the PKI private key certificate

    Returns:
        curl: the curl request
    """
    f = open('curl_template.txt', )
    curl = f.read()
    curl = curl.replace("SIGNATURE_PLACEHOLDER", signature)
    curl = curl.replace("PAYLOAD_PLACEHOLDER", payload)
    curl = curl.replace("CERTIFICATE_PLACEHOLDER", certificate)
    curl = curl.replace("CERTIFICATETYPE_PLACEHOLDER", certificateType)
    curl = curl.replace("PASSWORD_PLACEHOLDER", password)
    if (verbosity):
        curl = curl.replace("SILENT_PLACEHOLDER", "")
    else:
        curl = curl.replace("SILENT_PLACEHOLDER", "--silent")
    return curl

def createPDF(pdf, uvci):
    """Create a pdf with the result of the curl request

    Args:
        pdf: the pdf data sent back
        uvci: the uvci sent back - UVCI is the unique identifier of the covid certificate

    Returns:
        pdf_filename: the name of the created pdf

        """
    pdf_filename = uvci + ".pdf"
    f = open(pdf_filename, "wb")
    f.write(b64decode(pdf, validate=True))
    f.close()
    return pdf_filename