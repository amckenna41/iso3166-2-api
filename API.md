<a name="TOP"></a>

# ISO 3166-2 API 🌎

<!-- ![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-2) -->
![Vercel](https://vercelbadge.vercel.app/api/amckenna41/iso3166-2-api)

The main API endpoint is:

> [https://iso3166-2-api.vercel.app/api](https://iso3166-2-api.vercel.app/api)

The other endpoints available in the API are:
* https://iso3166-2-api.vercel.app/api/all
* https://iso3166-2-api.vercel.app/api/alpha/{input_alpha}
* https://iso3166-2-api.vercel.app/api/subdivision/{input_subdivision}
* https://iso3166-2-api.vercel.app/api/search/{input_search_name}
* https://iso3166-2-api.vercel.app/api/search_geo/{input_latlng}
* https://iso3166-2-api.vercel.app/api/country_name/{input_country_name}
* https://iso3166-2-api.vercel.app/api/list_subdivisions or https://iso3166-2-api.vercel.app/api/list_subdivisions/{input_alpha_code}
* https://iso3166-2-api.vercel.app/api/stats


* `/api`: main homepage and API documentation.

* `/api/all`: get all of the ISO 3166 subdivision data for all countries.

* `/api/alpha`: get all of the ISO 3166 subdivision data for 1 or more inputted ISO 3166-1 alpha-2, alpha-3 or numeric country codes, e.g. `/api/alpha/FR,DE,HU,ID,MA`, `/api/alpha/FRA,DEU,HUN,IDN,MAR` and `/api/alpha/428,504,638`. A comma separated list of multiple alpha codes can also be input. If an invalid country code is input then an error will be returned.

* `/api/subdivision`: get all of the ISO 3166 subdivision data for 1 or more ISO 3166-2 subdivision codes, e.g `/api/subdivision/GB-ABD`. You can also input a comma separated list of subdivision codes from the same and or different countries and the data for each will be returned e.g `/api/subdivision/IE-MO,FI-17,RO-AG`. If the input subdivision code is not in the correct format then an error will be raised. Similarly if an invalid subdivision code that doesn't exist is input then an error will be raised. **URL length limit:** passing very long comma-separated lists can exceed browser/server URL length limits (~2000 characters, roughly 100–150 codes). For bulk lookups beyond that, use the `POST /api/subdivision` endpoint which accepts a JSON body with a `codes` array of up to 500 codes.

* `/api/search/`: get all of the ISO 3166 subdivision data for 1 or more ISO 3166-2 subdivision names that match the inputted search terms, e.g `/api/search/Derry`, `/api/search/Kimpala`. You can also input a comma separated list of subdivision name from the same or different countries and the data for each will be returned e.g `/api/name/Paris,Frankfurt,Rimini`. A closeness function is utilised to find the matching subdivision name, if no exact name match found then the most approximate subdivisions will be returned. Some subdivisions may have the same name, in this case each subdivision and its data will be returned e.g `/api/name/Saint George` (this example returns 5 subdivisions). If an invalid subdivision name that doesn't match any is input then an error will be raised. The `likeness` and `excludeMatchScore` query string parameters can be used with this endpoint. 

* `/api/search_geo`: get all of the ISO 3166 subdivision data for subdivisions whose `latLng` attribute is approximately equal to the input latitude/longitude, e.g `/api/search_geo/39.4178,-2.6232`. A comma separated lat,lng string must be input. The optional `radius` query string parameter (in kilometers) controls the search radius; default is 50 km.

* `/api/country_name`: get all of the ISO 3166 subdivision data for 1 or more inputted ISO 3166-1 country names, as they are commonly known in English, e.g. `/api/country_name/France,Moldova,Benin`. A comma separated list of country names can also be input. A closeness function is utilised so the most approximate name from the input will be used e.g. Sweden will be returned if the input is `/api/country_name/Swede`. If no country is found from the closeness function or an invalid name is input then an error will be returned. The `likeness` query string parameter can be used with this endpoint.

* `/api/list_subdivisions`: get list of all the subdivision codes for all countries. You can also get the list of subdivisions from a subset of 
countries via their ISO 3166-1 country code.

* `/api/stats`: get live statistics about the ISO 3166-2 dataset — total countries, total subdivisions, countries with/without subdivisions, average subdivisions per country, flag coverage, and the current package version.

### Query String Parameters
There are several query string parameters that can be passed through several of the endpoints of the API:

* **likeness** (`?likeness=N`) - this is a value between 1 and 100 that increases or reduces the % of similarity/likeness that the 
inputted search terms have to match to the subdivision data in the subdivision code, name and local/other name attributes. This can be used with the `/api/search` and `/api/country_name` endpoints. Having a higher value should return more exact and less total matches and 
having a lower value will return less exact but more total matches, e.g ``/api/search/Paris?likeness=50``, 
``/api/country_name/Tajikist?likeness=90`` (default=100). **Note:** if using the `iso3166-2` Python package directly, the equivalent function parameter is named `likeness_score` (not `likeness`).
* **filterAttributes** - this is a list of the default supported attributes that you want to include in the output. By default all attributes will be returned but this parameter is useful if you only require a subset of attributes. Supported by **all data endpoints** including `/api/all`, e.g `api/all?filter=name,latLng`, `api/alpha/DEU?filter=latLng,flag`, `api/subdivision/PL-02?filter=localOtherName`.
* **excludeMatchScore** - this allows you to exclude the matchScore attribute from the search results when using the `/api/search endpoint`. The match score is the % of a match each returned subdivision data object is to the search terms, with 100% being an exact match. By default the match score is returned for each object, e.g `/api/search/Bucharest?excludeMatchScore=1`, ``/api/search/Oregon?excludeMatchScore=1`` (default=0).
* **limit** - this allows you to limit the total number of countries returned from the API call. This is only available in the `/api/all` endpoint. When calling the endpoint, all of the available data is called so this param allows you to get a faster small subset of the data. The first X country subdivision data will be returned. 
* **radius** - search radius in kilometers for the `/api/search_geo` endpoint. Default is 50 km.
* **format** (`?format=json|csv|geojson`) - output format for the response. Default is `json`. `csv` returns a downloadable CSV file with one row per subdivision. `geojson` returns a GeoJSON FeatureCollection with lat/lng stored as Point geometry (compatible with QGIS, Mapbox, Leaflet, etc.). Supported on `/api/all`, `/api/alpha`, `/api/subdivision`, `/api/search`, and `/api/country_name`.
* **lang** (`?lang=<ISO639code>`) - filter the `localOtherName` attribute to only include entries in the specified ISO 639 language code (e.g. `?lang=fra` for French, `?lang=deu` for German). Supported on all data endpoints, e.g `/api/all?lang=fra`, `/api/alpha/DE?lang=deu`.
* **page** (`?page=N`) - page number for paginated `/api/all` responses (1-indexed). Only activates pagination when `?page` or `?pageSize` is explicitly provided. The paginated response wraps the data in a `{"data": {...}, "page": N, "pageSize": N, "totalPages": N, "totalCountries": N}` envelope.
* **pageSize** (`?pageSize=N`) - number of countries per page for paginated `/api/all` responses. Accepts 1–250 (default 50).

> A demo of the software and API is available [here][demo].

Get ALL ISO 3166-2 subdivision data for ALL countries
-----------------------------------------------------
### Request
`GET /api/all`

    curl -i https://iso3166-2-api.vercel.app/api/all

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 20 Dec 2024 17:29:39 GMT
    server: Vercel
    content-length: 837958

    {"AD":..., "AE":...}

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/all"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = await fetch('https://iso3166-2-api.vercel.app/api/all')
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision data for a specific country, using its 2 letter alpha-2 code e.g FR, DE
------------------------------------------------------------------------------------------------------
### Request
`GET /api/alpha/FR`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/FR

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 20 Dec 2024 17:30:27 GMT
    server: Vercel
    content-length: 26298

    {"FR":{"FR-01":{...}}}

### Request
`GET /api/alpha/DE`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/DE

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 20 Dec 2024 17:31:19 GMT
    server: Vercel
    content-length: 3053

    {"DE":{"DE-BB":{...}}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/alpha/"
input_alpha2 = "FR" #DE

request_url = f'{base_url}{input_alpha2}'

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha2 = "FR"; //DE

function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/alpha/${input_alpha2}`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision data for a specific country, using its 3 letter alpha-3 code e.g CZE, HRV
--------------------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/CZE`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/CZE

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 20 Dec 2024 17:42:24 GMT
    server: Vercel
    content-length: 14266

    {"CZ":{"CZ-10":{"..."}}}

### Request
`GET /api/alpha/HRV`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/HRV

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 20 Dec 2024 17:46:12 GMT
    server: Vercel
    content-length: 5456

    {"HR":{"HR-01":{"..."}}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/alpha/"
input_alpha3 = "CZE" #HRV

request_url = f'{base_url}{input_alpha3}'

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_alpha3 = "CZE"; //HRV

function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/alpha/${input_alpha3}`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision data for a specific country, using its numeric code e.g 268, 398
-----------------------------------------------------------------------------------------------

### Request
`GET /api/alpha/268`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/268

### Response
    HTTP/2 200 
    content-type: application/json
    date: Fri, 22 Dec 2024 18:20:14 GMT
    server: Vercel
    content-length: 1899

    {"GE":{"GE-AB":{"..."}}}

### Request
`GET /api/alpha/398`

    curl -i https://iso3166-2-api.vercel.app/api/alpha/398

### Response
    HTTP/2 200 
    content-type: application/json
    date: Fri, 22 Dec 2024 19:40:10 GMT
    server: Vercel
    content-length: 2922

    {"KZ":{"KZ-10":{"..."}}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/alpha/"
input_numeric = "268" #398

request_url = f'{base_url}{input_numeric}'

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_numeric = "268"; //398

function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/alpha/${input_numeric}`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision data for a specific subdivision, using its subdivision code e.g LV-007, PA-3, ZA-NC
------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/subdivision/LV-007`

    curl -i https://iso3166-2-api.vercel.app/api/subdivision/LV-007

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 11:25:52 GMT
    server: Vercel
    content-length: 244

    {"LV-007":{"flag":"https://github.com/amckenna41/...}}

### Request
`GET /api/subdivision/PA-3`

    curl -i https://iso3166-2-api.vercel.app/api/subdivision/PA-3

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 11:28:02 GMT
    server: Vercel
    content-length: 214

    {"PA-3":{"flag":"https://github.com/amckenna41...}}

### Request
`GET /api/subdivision/ZA-NC`

    curl -i https://iso3166-2-api.vercel.app/api/subdivision/ZA-NC

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 11:37:04 GMT
    server: Vercel
    content-length: 225

    {"ZA-NC":{"flag":"https://github.com/amckenna41...}}


Search for ISO 3166-2 subdivision data using its subdivision name or local/other name e.g Treviso (IT-TV), Nordland (NO-18), Musandam (OM-MU)
--------------------------------------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/search/Treviso`

    curl -i https://iso3166-2-api.vercel.app/api/search/Treviso

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 13:02:10 GMT
    server: Vercel
    content-length: 215

    {"IT-TV":{"flag":"}}

### Request
`GET /api/search/Nordland`

    curl -i https://iso3166-2-api.vercel.app/api/search/Nordland

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 13:07:01 GMT
    server: Vercel
    content-length: 212

    {"NO-18":{"flag":"}}

### Request
`GET /api/search/Musandam`

    curl -i https://iso3166-2-api.vercel.app/api/search/Musandam

### Response
    HTTP/2 200 
    content-type: application/json
    date: Mon, 29 Jan 2025 13:11:09 GMT
    server: Vercel
    content-length: 132

    {"OM-MU":{"flag":}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/search/"
input_subdivision_name = "Treviso" #Nordland, Musandam

request_url = f'{base_url}{input_subdivision_name}'
params={"likeness":"90"} #pass a likeness score of 90 to the request

all_request = requests.get(request_url, params=params)
all_request.json() 
```

### Javascript
```javascript
let input_subdivision_name = "Treviso"; //Nordland, Musandam
let params = {"likeness": "90"} //pass a likeness score of 90 to the request

function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/search/${input_subdivision_name}?likeness=${params.likeness}`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Search for ISO 3166-2 subdivision data using approximate latitude/longitude coordinates e.g 39.4178,-2.6232
------------------------------------------------------------------------------------------------------------

### Request
`GET /api/search_geo/39.4178,-2.6232`

        curl -i https://iso3166-2-api.vercel.app/api/search_geo/39.4178,-2.6232

### Response
        HTTP/2 200 
        content-type: application/json
        date: Mon, 29 Jan 2025 13:22:10 GMT
        server: Vercel
        content-length: 214

        {"ES-CM":{"flag":"https://github.com/amckenna41...}}

    ### Example
    `GET /api/search_geo/28.2936,-16.6214?radius=50`

        curl -i https://iso3166-2-api.vercel.app/api/search_geo/28.2936,-16.6214?radius=50

### Request
`GET /api/search_geo/37.9567,-4.8477?radius=25`

        curl -i https://iso3166-2-api.vercel.app/api/search_geo/37.9567,-4.8477?radius=25

### Response
        HTTP/2 200 
        content-type: application/json
        date: Mon, 29 Jan 2025 13:23:01 GMT
        server: Vercel
        content-length: 225

        {"ES-CO":{"flag":"https://github.com/amckenna41...}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/search_geo/"
input_latlng = "39.4178,-2.6232" #37.9567,-4.8477

request_url = f'{base_url}{input_latlng}'
params={"radius":"25"} #optional radius in km

all_request = requests.get(request_url, params=params)
all_request.json() 
```

### Javascript
```javascript
let input_latlng = "39.4178,-2.6232"; //37.9567,-4.8477
let params = {"radius": "25"} //optional radius in km

function getData() {
    const response = 
        await fetch(`https://iso3166-2-api.vercel.app/api/search_geo/${input_latlng}`, params); 
    const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get a random ISO 3166-2 subdivision
-----------------------------------

### Request
`GET /api/random`

        curl -i https://iso3166-2-api.vercel.app/api/random

### Response
        HTTP/2 200 
        content-type: application/json
        date: Mon, 29 Jan 2025 13:30:10 GMT
        server: Vercel
        content-length: 214

        {"DE-BE":{"flag":"https://github.com/amckenna41...}}

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/random"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
    const response = 
        await fetch('https://iso3166-2-api.vercel.app/api/random'); 
    const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision data for a specific country, using country name, e.g. Tajikistan (TJ), Seychelles (SC), Uganda (UG) 
----------------------------------------------------------------------------------------------------------------------------------

### Request
`GET /api/country_name/Tajikistan`

    curl -i https://iso3166-2-api.vercel.app/api/country_name/Tajikistan

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sat, 23 Dec 2024 14:01:19 GMT
    server: Vercel
    content-length: 701

    {"TJ":{"TJ-DU":{...}}}

### Request
`GET /api/country_name/Seychelles`

    curl -i https://iso3166-2-api.vercel.app/api/country_name/Seychelles

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sat, 23 Dec 2024 14:15:53 GMT
    server: Vercel
    content-length: 5085

    {"SC":{"SC-01":{...}}}

### Request
`GET /api/country_name/Uganda`

    curl -i https://iso3166-2-api.vercel.app/api/country_name/Uganda

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sat, 23 Dec 2024 14:17:39 GMT
    server: Vercel
    content-length: 14965

    {"UG":{"UG-101":{...}}}

### Python
```python
import requests

base_url = "https://iso3166-2-api.vercel.app/api/country_name/"
input_name = "Tajikistan" #Seychelles, Uganda

request_url = f'{base_url}{input_name}'

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
let input_name = "Tajikistan"; //Seychelles, Uganda

function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/country_name/${input_name}`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision codes for all countries, or subset of countries
-------------------------------------------------------------------

### Request
`GET /api/list_subdivisions`

    curl -i https://iso3166-2-api.vercel.app/api/list_subdivisions

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sat, 03 Feb 2025 15:03:11 GMT
    server: Vercel
    content-length: 

    {"AD":{"AD-02","AD-03"...}}

### Request
`GET /api/list_subdivisions/LK`

    curl -i https://iso3166-2-api.vercel.app/api/list_subdivisions/LK

### Response
    HTTP/2 200 
    content-type: application/json
    date: Sat, 04 Feb 2025 15:01:12 GMT
    server: Vercel
    content-length: 

    {"LK":{"LK-1","LK-1"...}}

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/list_subdivisions"
#request_url = "https://iso3166-2-api.vercel.app/api/list_subdivisions/LK"

all_request = requests.get(request_url)
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = 
    await fetch(`https://iso3166-2-api.vercel.app/api/list_subdivisions`); 
    // await fetch(`https://iso3166-2-api.vercel.app/api/list_subdivisions/LK`); 
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Get all ISO 3166-2 subdivision codes for all countries, filtering and only returning the name and localOtherName attributes
---------------------------------------------------------------------------------------------------------------------------
### Request
`GET /api/all`

    curl -i https://iso3166-2-api.vercel.app/api/all?filter=name,localOtherName

### Response
    HTTP/2 200 
    content-type: application/json
    date: Wed, 10 May 2025 14:22:31 GMT
    server: Vercel
    content-length: X

    {"AD":..., "AE":...}

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/all"

all_request = requests.get(request_url, params={"filter": "name, localOtherName"})
all_request.json() 
```

### Javascript
```javascript
function getData() {
  const response = await fetch('https://iso3166-2-api.vercel.app/api/all?filter=name,localOtherName')
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

[Back to top](#TOP)

Get live statistics about the ISO 3166-2 dataset
-------------------------------------------------
### Request
`GET /api/stats`

    curl -i https://iso3166-2-api.vercel.app/api/stats

### Response
    HTTP/2 200
    content-type: application/json
    date: Wed, 14 May 2026 10:00:00 GMT
    server: Vercel

    {
      "totalCountries": 249,
      "totalSubdivisions": 5046,
      "countriesWithSubdivisions": 200,
      "countriesWithoutSubdivisions": 49,
      "averageSubdivisionsPerCountry": 25.23,
      "maxSubdivisions": {"country": "GB", "count": 221},
      "minSubdivisions": {"country": "AD", "count": 7},
      "flagCoverage": {"count": 3501, "percentage": 69.4},
      "packageVersion": "1.8.2"
    }

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/stats"

stats_request = requests.get(request_url)
stats_request.json()
```

### Javascript
```javascript
function getData() {
  const response = await fetch('https://iso3166-2-api.vercel.app/api/stats')
  const data = await response.json()
}

// Begin accessing JSON data here
var data = JSON.parse(this.response)
```

Bulk subdivision lookup using a POST request
--------------------------------------------
Use `POST /api/subdivision` when you need to look up more codes than a URL can comfortably hold
(roughly 100–150 codes before hitting browser/server URL length limits).

### Request
`POST /api/subdivision`

    curl -i -X POST https://iso3166-2-api.vercel.app/api/subdivision \
      -H "Content-Type: application/json" \
      -d '{"codes": ["GB-ABD", "FR-75", "US-CA", "DE-BY"]}'

### Response
    HTTP/2 200
    content-type: application/json

    {"DE": {"DE-BY": {...}}, "FR": {"FR-75": {...}}, "GB": {"GB-ABD": {...}}, "US": {"US-CA": {...}}}

### Python
```python
import requests

request_url = "https://iso3166-2-api.vercel.app/api/subdivision"
codes = ["GB-ABD", "FR-75", "US-CA", "DE-BY"]  # up to 500 codes

post_request = requests.post(request_url, json={"codes": codes})
post_request.json()
```

### Javascript
```javascript
const codes = ["GB-ABD", "FR-75", "US-CA", "DE-BY"]; // up to 500 codes

async function getData() {
  const response = await fetch('https://iso3166-2-api.vercel.app/api/subdivision', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ codes })
  });
  const data = await response.json();
}
```

[Back to top](#TOP)

[demo]: https://colab.research.google.com/drive/1btfEx23bgWdkUPiwdwlDqKkmUp1S-_7U?usp=sharing