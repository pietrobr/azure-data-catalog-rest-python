import json
import adal
import uuid
import requests 

catalogName = "DefaultCatalog"
clientIDFromAzureAppRegistration = "<Application ID of your Web app/API in AAD>"
tenantId = "<Tenant ID>"
spsecret = "<Application Key of your Web app/API>"
resourceUri = "https://api.azuredatacatalog.com"
redirectUri = "https://login.live.com/oauth20_desktop.srf"
authorityUri = "https://login.windows.net/{0}".format (tenantId)
registerUri = "https://api.azuredatacatalog.com/catalogs/{0}/views/tables?api-version=2016-03-30".format(catalogName)
upn = clientIDFromAzureAppRegistration + "@" + tenantId
searchTerm = "OrdersSample"

context = adal.AuthenticationContext(authorityUri, validate_authority=authorityUri != 'adfs',)
token = context.acquire_token_with_client_credentials(
    resourceUri,
    clientIDFromAzureAppRegistration,
    spsecret)
accessToken = token['accessToken']

def registerDataAsset(jsonasset):
    resp = setRequestAndGetResponse(registerUri, jsonasset)
    dataAssetHeader = resp.headers["Location"]
    return dataAssetHeader

def sampleJson(name, upn):
    return """{{
    "properties" : {{
        "fromSourceSystem" : false,
        "name": "{0}",
        "dataSource": {{
            "sourceType": "SQL Server",
            "objectType": "Table",
        }},
        "dsl": {{
            "protocol": "tds",
            "authentication": "windows",
            "address": {{
                "server": "test.contoso.com",
                "database": "Northwind",
                "schema": "dbo",
                "object": "{0}"
            }}
        }},
        "lastRegisteredBy": {{
            "upn": "{1}"
        }},
    }},
    "annotations" : {{
        "schema": {{
            "properties" : {{
                "fromSourceSystem" : false,
                "columns": [
                    {{
                        "name": "OrderID",
                        "isNullable": false,
                        "type": "int",
                        "maxLength": 4,
                        "precision": 10
                    }},
                    {{
                        "name": "CustomerID",
                        "isNullable": true,
                        "type": "nchar",
                        "maxLength": 10,
                        "precision": 0
                    }},
                    {{
                        "name": "OrderDate",
                        "isNullable": true,
                        "type": "datetime",
                        "maxLength": 8,
                        "precision": 23
                    }},
                ],
            }}
        }},
        "previews": [
          {{
                "properties": {{
                    "preview": [
                      {{
                        "OrderId": 1,
                        "CustomerID": 11,
                        "OrderDate": null
                      }},
                      {{
                        "OrderId": 2,
                        "CustomerID": 12,
                        "OrderDate": "08/02/2017"
                      }}
                    ],
                    "key": "SqlExtractor",
                    "fromSourceSystem": true
                }}
          }}
        ],
        "tableDataProfiles": [
          {{
            "properties": {{
              "dataModifiedTime": "2015 -12-31T00:32:22.4832805-08:00",
              "schemaModifiedTime": "2015 -12-31T00:32:22.4832805-08:00",
              "size": 9223372036854775807,
              "numberOfRows": 9223372036854775807,
              "key": "Test",
              "fromSourceSystem": true
            }}
          }}
        ],
        "columnsDataProfiles": [
          {{
            "properties": {{
              "columns": [
                {{
                  "columnName": "OrderId",
                  "type": "int",
                  "min": "1",
                  "max": "1002",
                  "stdev": 50,
                  "avg": 201,
                  "nullCount": 0,
                  "distinctCount": 12121212
                }}
              ],
              "key": "Test",
              "fromSourceSystem": true
            }}
          }}
        ],
    }}
    }}""".format(name, upn)

def setRequestAndGetResponse(url, payload):
    while True:
        http_headers = getHeadersAuth()
        if(payload is None):
            r = requests.get(url, headers=http_headers, allow_redirects=False) 
        else:
            r = requests.post(url, headers=http_headers, data=payload, allow_redirects=False) 
        
        if(r.status_code >= 301 and r.status_code <= 399):
            redirectedUrl = r.headers["Location"]
            url = redirectedUrl
            r = None
        else:
            return r

def getHeadersAuth():
    http_headers = {'Authorization': 'Bearer ' + accessToken,
                    'Content-Type': 'application/json; charset=utf-8'
                    }
    return http_headers

def searchDataAsset(searchTerm):
    fullUri = "https://api.azuredatacatalog.com/catalogs/{0}/search/search?searchTerms={1}&count=10&api-version=2016-03-30".format(catalogName, searchTerm)
    resp = setRequestAndGetResponse(fullUri, None)
    return resp.text

def deleteAsset(dataAssetUrl):
    http_headers = getHeadersAuth()
    fullUri = "{0}?api-version=2016-03-30".format(dataAssetUrl)
    r = requests.delete(fullUri, headers=http_headers)
    return str(r.status_code)

#Registration
asset = sampleJson("OrdersSample" + str(uuid.uuid4()), upn)
id = registerDataAsset(asset)
print("REG:" + id)

#Search
searchJson = searchDataAsset(searchTerm)
print("SER:" + searchJson)

#Delete
d = deleteAsset(id)
print("DEL:" + d)