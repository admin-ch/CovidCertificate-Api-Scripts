# JavaScript Scripts to use the Swiss Covid Certificate API

The script [`request.js`](request.js) allows you to generate Covid certificates. The script is provided as is.
It was developed for demo purposes only. It was tested with node v14.17.0 on macOS.

## Prerequisites

1. You have an access to [test web management UI](https://www.covidcertificate-a.admin.ch/))
2. You have received a PKI certificate (.cer and .key files) of the type ["SwissGov Regular CA 01"](https://www.bit.admin.ch/bit/en/home/subsites/allgemeines-zur-swiss-government-pki/rootzertifikate/swiss-government-root-ca-ii.html)
3. You have Node.js installed and running.

## Setup

1. Run `npm install` to install the dependencies.
2. Adapt the configuration variables for the `certificateFile` and `keyFile`.

## Procedure

1. Obtain a one time password from Web management UI.
2. Pass the OTP and keyPassPhrase via the enviroment to the script and start it:

```bash
export CC_CLI_OTP=a.b.c
export CC_CLI_KEY_PASSPHRASE=secret
node script.js
```

3. See the links to the generated PDF and PNG in the CLI output.

## Other Node.js samples

We have created a demo CLI application using Node.js and Typescript. You will find it at: <https://github.com/admin-ch/CovidCertificate-Api-Cli>.
