# .NET demo app to use the Swiss Covid Certificate API

The demo app [`Program.cs`](Program.cs) shows how to generate Covid certificates. It is provided as is.
It was developed for demo purposes only. It was tested with dotnet v5.0.103 on Windows.

## Prerequisites

1. You have an access to [test web management UI](https://www.covidcertificate-a.admin.ch/))
2. You have received a PKI certificate (.cer and .key files) of the type ["SwissGov Regular CA 01"](https://www.bit.admin.ch/bit/en/home/subsites/allgemeines-zur-swiss-government-pki/rootzertifikate/swiss-government-root-ca-ii.html)
3. You have a .NET 5 environment .

## Procedure

1. Adapt the configuration variables for the `certificateFile` and `keyFile`.
2. Obtain a one time password (OTP) from Web management UI.
3. Configure the environment variables, for example via a `launchSetting.json`:

```json
"environmentVariables": {
  "CC_CLI_CERTIFICATE_FILE_P12": "-- path to your .p12 --",
  "CC_CLI_KEY_PASSPHRASE": "-- certificate password --",
  "CC_CLI_OTP": "-- otp from the web UI",
}
```

4. See the links to the generated PDF and PNG in the CLI output.
