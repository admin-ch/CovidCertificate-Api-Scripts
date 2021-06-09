using System;
using System.IO;
using System.Net.Http;
using System.Reflection;
using System.Reflection.Metadata.Ecma335;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace CC_API
{
    class Program
    {
        static async Task<int> Main(string[] args)
        {
            // configuration
            var outDir = "out";
            var baseUrl = "https://ws.covidcertificate-a.bag.admin.ch/";
            // path to the .p12 file from the tls certificate zip
            var certificateFile = Environment.GetEnvironmentVariable("CC_CLI_CERTIFICATE_FILE_P12");
            // we send that password per SMS, it is also used to unzip the certificate
            var passphrase = Environment.GetEnvironmentVariable("CC_CLI_KEY_PASSPHRASE");
            // acquire via the UI https://www.covidcertificate-a.admin.ch/otp
            var otp = Environment.GetEnvironmentVariable("CC_CLI_OTP");
    

            if (string.IsNullOrWhiteSpace(certificateFile))
                throw new Exception($"Environment variable 'CC_CLI_CERTIFICATE_FILE_P12' not set.");
            if (string.IsNullOrWhiteSpace(passphrase))
                throw new Exception($"Environment variable 'CC_CLI_KEY_PASSPHRASE' not set.");
            if (string.IsNullOrWhiteSpace(otp))
                throw new Exception($"Environment variable 'CC_CLI_OTP' not set.");

            // load the certificate - could also be loaded via X509Store
            var certificate = new X509Certificate2(certificateFile, passphrase);
            if (!certificate.HasPrivateKey) throw new Exception("Certificate does not have a private key.");

            // create the JSON 

            var recovery = new
            {
                name = new { familyName = "Rochat", givenName = "Céline" },
                dateOfBirth = "1964-03-14",
                language = "fr",
                recoveryInfo = new[] { new { dateOfFirstPositiveTestResult = "2021-05-21", countryOfTest = "CH" } },
                otp = otp
            };

            var json = JsonSerializer.Serialize(recovery, new JsonSerializerOptions() { WriteIndented = true });

            // create the signature for the content integrity check, see: https://github.com/admin-ch/CovidCertificate-Apidoc#content-signature
            var regex = new Regex("[\\n\\r\\t ]", RegexOptions.Multiline);
            var canonicalJson = regex.Replace(json, string.Empty);
            var canonicalPayload = Encoding.UTF8.GetBytes(canonicalJson);
            var rsaPrivateKey = certificate.GetRSAPrivateKey();
            byte[] signatureBytes = rsaPrivateKey.SignData(canonicalPayload, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
            var signature = Convert.ToBase64String(signatureBytes);

            // create the http request
            var request = new HttpRequestMessage()
            {
                RequestUri = new Uri($"{baseUrl}api/v1/covidcertificate/recovery"),
                Method = HttpMethod.Post,
                Headers = { {"X-Signature", signature } },
                Content = new StringContent(json, Encoding.UTF8, "application/json"),
            };

            // configure the HttpClient to use the client authentication certificate
            var handler = new HttpClientHandler() { ClientCertificates = { certificate }};
            var client = new HttpClient(handler);

            // send the request
            var response = await client.SendAsync(request);
            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Request failed: {response.StatusCode} - {response.ReasonPhrase}");
                var message = await response.Content.ReadAsStringAsync();
                Console.WriteLine(message);
                return 1;
            }

            var responseStream = await response.Content.ReadAsStreamAsync();
            var createdResponse = await JsonSerializer.DeserializeAsync<CreatedCertificateDto>(responseStream);

            var uvci = createdResponse.uvci;
            
            Directory.CreateDirectory(outDir);
            await saveFile(uvci, createdResponse.pdf, ".pdf");
            await saveFile(uvci, createdResponse.qrCode, ".png");

            async Task saveFile (string uvci, string base64, string extension) 
            {
                var fileName = uvci.Replace(":", "_");
                var path = Path.Combine(outDir, fileName + extension);
                await File.WriteAllBytesAsync(path, Convert.FromBase64String(base64));
                Console.WriteLine($"Written: {path}");
            }
            
            return 0;
        }

        private class CreatedCertificateDto
        {
            public string uvci { get; set; }
            public string pdf { get; set; }
            public string qrCode { get; set; }
        }
    }
}
