#!/usr/bin/env node

// configuration
const baseUrl = 'https://ws.covidcertificate-a.bag.admin.ch/'
const certificateFile = 'ZH-spital-A-t.bit.admin.ch.cer'
const keyFile = 'ZH-spital-A-t.bit.admin.ch.encrypted.key'
// we send that password per SMS, it is also used to unzip the certificate
const keyPassphrase = process.env.CC_CLI_KEY_PASSPHRASE
// acquire via the UI https://www.covidcertificate-a.admin.ch/otp
const otp = process.env.CC_CLI_OTP
const outDir = 'out'


const path = require('path')
const https = require('https')
const crypto = require('crypto')
const fs = require('fs-extra')
const axios = require('axios').default

async function canonicalizeAndSign (json) {
  // the canonicalization regex is defined by the API
  const regex = /[\n\r\t ]/gm
  const canonicalMessage = json.replace(regex, '')

  const bytes = Buffer.from(canonicalMessage, 'utf8')
  const pemEncodedKey = await fs.readFile(keyFile)
  const privateKeyObject = crypto.createPrivateKey({ key: pemEncodedKey, passphrase: keyPassphrase })
  const sign = crypto.createSign('RSA-SHA256')
  sign.update(bytes)
  const signature = sign.sign(privateKeyObject)
  return signature.toString('base64')
}

async function setupAxiosHttpClient () {
  const pemEncodedKey = await fs.readFile(keyFile)
  const pemEncodedCertificate = await fs.readFileSync(certificateFile)

  return axios.create({
    baseURL: baseUrl,
    // TLS client certificate auth
    httpsAgent: new https.Agent({
      cert: pemEncodedCertificate,
      key: pemEncodedKey,
      passphrase: keyPassphrase
    })
  })
}

async function saveFile (base64, uvci, extension) {
  await fs.ensureDir('out')
  const file = path.join(outDir, `${uvci.replace(/:/g, '_')}${extension}`)
  const data = Buffer.from(base64, 'base64')
  await fs.writeFile(file, data)
  console.log(`Output: ${file}`)
}

async function main () {
  const dto = {
    otp: otp,
    name: {
      familyName: 'Rochat',
      givenName: 'Céline'
    },
    dateOfBirth: '1964-03-14',
    testInfo: [
      {
        typeCode: 'LP6464-4',
        sampleDateTime: '2020-01-01T17:29:41Z',
        testingCentreOrFacility: 'Centre de test de Payerne',
        memberStateOfTest: 'CH'
      }
    ],
    language: 'fr'
  }

  // intend json to show canonicalization
  const json = JSON.stringify(dto, null, 2)
  const signature = await canonicalizeAndSign(json)

  try {
    const config = { headers: { 'X-Signature': signature } }
    const instance = await setupAxiosHttpClient()
    const res = await instance.post('api/v1/covidcertificate/test', dto, config)
    await saveFile(res.data.pdf, res.data.uvci, '.pdf')
    await saveFile(res.data.qrCode, res.data.uvci, '.png')
  } catch (error) {
    if (error.response) {
      const res = error.response
      console.error(`> ${res.status} - ${JSON.stringify(res.data)}`)
      console.log(`> x-vcap-request-id: ${res.headers['x-vcap-request-id']}`)
    } else {
      console.error(error.message)
    }
  }
}

main().then(() => {
  console.log('done')
}).catch(err => {
  console.error(err)
})
