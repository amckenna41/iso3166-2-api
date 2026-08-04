# Change Log 

## 1.8.4 - July/August 2026

### Added

- Added CORS support (`Access-Control-Allow-Origin: *`) to all responses, so the API can now be called directly from browser JavaScript on any origin without a proxy
- Added `ETag` headers and `If-None-Match` revalidation to successful GET data responses, returning a 304 Not Modified instead of re-sending the payload (notable for `/api/all`, which is ~2.6MB)
- Added response caching to the `/api/coords` reverse geocoding lookups, keyed on coordinates rounded to ~100m, to stay within the OpenStreetMap Nominatim usage policy
- Added an offline fallback to `/api/coords` that returns the geographically closest subdivision from the local dataset when Nominatim is unavailable or has no ISO 3166-2 code for the location, so a valid coordinate always returns a result
- Added rate limiting to `/api/coords` (30 requests per minute per IP, configurable via the `COORDS_RATE_LIMIT` environment variable), returning a 429 when exceeded
- Added `?format` support to `/api/search_geo`, `POST /api/subdivision` and `/api/list_subdivisions` (json/csv only on the latter, as it returns codes rather than attributes)
- Added `?lang` support to `/api/search_geo` and `POST /api/subdivision`
- Added `?format` and `?lang` support to `/api/coords` and `/api/random`, the last two data endpoints that were silently ignoring both
- Added rate limiting to `/api/all` (300 requests per minute per IP, configurable via the `ALL_RATE_LIMIT` environment variable), as it returns the entire ~2.6MB dataset in a single response. Deliberately generous, it is intended to bound abuse rather than throttle normal use
- Added spreadsheet formula injection protection to the CSV output, prefixing any cell beginning with `=`, `+`, `-`, `@`, tab or carriage return with a quote so it is not evaluated when the file is opened in Excel, LibreOffice or Sheets
- Added `X-Page`, `X-Page-Size`, `X-Total-Pages` and `X-Total-Countries` response headers to paginated `/api/all` responses in `csv` and `geojson` format, which have no envelope to carry the metadata
- Added `/api/stats`, `/api/version`, `/api/clear-cache` and `POST /api/subdivision` to the OpenAPI spec, which previously documented none of them
- Added a TTL to the `/api/coords` reverse geocoding cache (24 hours, configurable via the `REVERSE_GEOCODE_TTL` environment variable). `lru_cache` has no expiry of its own, so a result was previously pinned for the lifetime of a warm instance
- Added unit tests for all of the above to the local test suite

### Changed

- **Breaking:** `/api/clear-cache` is now a POST endpoint requiring the token in an `X-Cache-Clear-Token` header, rather than a GET with a `?token` query string parameter, so the token no longer appears in access logs or browser history
- The `/api/clear-cache` token is now compared using `hmac.compare_digest` to prevent recovering it via response timing
- Flask debug mode is now opt-in via the `FLASK_DEBUG` environment variable rather than being hardcoded on, resolving the Bandit HIGH severity finding
- Pinned all dependencies to upper version bounds so an upstream breaking release cannot reach production without an explicit bump
- Consolidated the duplicated `?lang` and `?format` parsing across endpoints into shared `apply_lang` and `apply_format` helpers, so validation cannot drift between endpoints
- Documented the previously undocumented `?limit` parameter, and the `?format`, `?lang`, `?limit`, `?page` and `?pageSize` parameters are now present in the OpenAPI spec
- Moved the `if __name__ == '__main__'` block to the end of the test module; it previously sat above the local test class, so running the file directly never executed those tests
- **Breaking:** `/api/version` now returns a JSON object, `{"version": "1.8.4"}`, rather than a bare string served as `text/html`, so callers no longer have to special case this endpoint against every other one
- Updated the required version of the `iso3166-2` package to 1.8.4
- The `iso3166-2` package's `". Did you mean: X, Y, Z?"` suggestion is now stripped in the shared `create_error_message` helper rather than in a single endpoint, so `/api/alpha` and `/api/list_subdivisions` no longer report the same invalid country code differently
- `/api/search` no longer returns the `code` attribute that the package's `search()` adds, as it just repeats the subdivision code the result is already keyed by and is not returned by any other endpoint or accepted by `?filter`
- The client IP used for rate limiting is now taken from `X-Vercel-Forwarded-For`/`X-Real-IP`, or the last `X-Forwarded-For` entry, rather than the first
- The test suite now starts the Flask app on a local port and runs against that by default, so it tests the code in the working tree rather than whatever is currently deployed, and is not blocked by the bot protection in front of the live deployment. Set `ISO3166_2_API_URL` to test a deployed instance instead

### Fixed

- Fixed `filter_attributes` mutating the module level `all_attributes` list. A single `?filter=*&excludeMatchScore=0` request permanently appended `matchScore`, `countryCode` and `subdivisionCode` to the global list, which then leaked across all subsequent requests on a warm serverless instance and caused those names to be wrongly accepted as filter attributes on every endpoint
- Fixed five country name aliases being unreachable because the lookup was keyed on `.title()` cased input while the alias map held non title-case keys. `UAE` and `USA` returned a 400, and `DR Congo` silently returned data for Congo (CG) instead of the Democratic Republic of the Congo (CD). Also affected `Sao Tome and Principe` and `French Southern and Antarctic Lands`
- Fixed `?lang` validation being inconsistent between endpoints. Only `/api/alpha` validated the code against ISO 639, so an unrecognised code such as `?lang=zzz` returned a 200 with every `localOtherName` silently nulled out on `/api/all`, `/api/country_name` and `/api/subdivision`. All data endpoints now return a 400
- Fixed an unhandled exception in `/api/coords` when the reverse geocoding provider returned a non-JSON body (e.g. a rate limit or gateway error page), which raised out of the handler as a 500
- Fixed `?format` and `?lang` being silently ignored on `/api/search` when `excludeMatchScore=0`, as results are returned as a list rather than a nested object in that mode
- Fixed `openapi.yaml` not being valid YAML. Unquoted response descriptions containing commas inside flow mappings, plus an unquoted `{country_code: ...}` brace, meant the spec served at `/openapi.yaml` could not be parsed by any OpenAPI tooling such as Swagger UI or client generators
- Fixed `?filter` emptying out every `history` entry. The attribute filter recursed into the value of each attribute it kept, so the keys of the nested history objects (`Change`, `Date Issued`, `Description of Change`, `Source`) were themselves filtered out and `history` came back as `[{}]`. This also affected `?filter=*`, which is documented as returning everything, so any caller using the wildcard silently lost all history data
- Fixed the rate limit being trivially bypassable. The client IP was read from the first `X-Forwarded-For` entry, which is whatever the caller sent rather than what a proxy wrote, so rotating the header reset the counter on every request. This left `/api/coords` able to drive unlimited requests at the OpenStreetMap Nominatim service through the deployment IP, risking a ban
- Fixed the rate limiter wiping every caller's counter when its key dictionary exceeded 10,000 entries. It cleared the whole dictionary, including callers currently being limited, so a burst of unique keys reset the limiter on demand. Only keys whose window has fully expired are now evicted
- Fixed `/api/random` being cached. The blanket `Cache-Control: public, max-age=3600` applied to it too, so the CDN in front of the API served the same "random" subdivision to every caller for an hour. It is now returned with `Cache-Control: no-store`
- Fixed `?page` and `?pageSize` being silently ignored when combined with `?format=csv` or `?format=geojson` on `/api/all`, which serialised the entire dataset instead of the requested page. Pagination is now applied before the format conversion
- Fixed the `/api/coords` 500 handler returning the raw exception text to the caller, which can carry internal paths and state. The detail is now logged and a generic message returned
- Fixed path inputs being URL decoded twice on `/api/search`, `/api/search_geo`, `/api/country_name` and `/api/subdivision`. Flask has already decoded the path segment, so a second decode let a caller smuggle another layer of encoding through, e.g. `%2541` arriving as `A` rather than `%41`
- Fixed a `ResourceWarning` from the test suite, which left the file handle returned by `send_from_directory` for `/openapi.yaml` unclosed
- Updated the `/api/search` match score expectations in the test suite for the rescored fuzzy matching in `iso3166-2` 1.8.4, and stopped asserting the exact order of equally scored results, which the package does not guarantee

## 1.8.1/v1.8.2 - Feb 2026

### Added

- Added /spec & /openapi.yml endpoints on API, added unit tests
- Added /random endpoint on API that returns a random subdivision from the >5000 available, added unit tests
- Added additional caching 
- Added /search_geo endpoint which allows you to search for a subdivision via its coordinates
- Added iso3166-2 logo

### Changed
- Change use of python-iso3166 library to pycountry


### Fixed


## 1.6.0-1.7.2 - June 2024 - July 2025


### Added
- Added list_subdivisions endpoint that returns all subdivision codes for all countries - API.md and unit tests updated
- Programmatically get software version and last updated from PyPI server, add unit tests to test this
- Parameter typing
- Added filter query string parameter and accompanying function, allowing for subdivisions and their specific attributes to be returned, e.g "?filter=name,type" will return all subdivisions but just the name and type attributes for each. This functionality has been added to each endpoint
- Added new unit tests for the filter query string parameter
- For filter query string parameter, inputting a wildcard symbol "*" as its value will return all attributes for the subdivision
- Query string parameter section added to the api homepage, including a quick description for the supported parameters
- Added a dev only endpoint called '/clear-cache that clears the cached Subdivision class instance and any subdivision data
- Added a dev only endpoint called /version that outputs the current version of the iso3166-2 software currently being used
- Added Open API Swagger spec, file and endpoint

### Changed
- Reorder credits and contributing section on api homepage
- Switched to f string formatting 
- Error message now returned for endpoints when no parameter input to them, previously the 404 page was returned
- Changed thefuzz python library scorer ratio parameter value for subdivision and country name endpoint
- If no valid subdivision name found after searching via its respective endpoint, update to error message to include suggestion of reducing the likeness value
- Upgraded checkout action in workflow from v3 to v4
- Set the error message path object val at top of each endpoint rather than repeating 
- Output error message for /name endpoint now includes the current likeness score that is returning invalid matches
- API.md abd examples updated with new filter query string parameter
- Renaming any references of localName to localOtherName, updating any descriptions about local name to include other names as well
- Copied API frontend code from iso3166-updates-api to this API
- Removed convert_to_alpha2 function from main flask app, conversion now done in main iso3166-2 software
- Updated all error return messages in API to use the create_error_message function
- Programmatically get the Last Updated value on API homepage
- Reordered sections in index.html
- Updated all references of iso3166-flag-icons to iso3166-flags

### Fixed 
- Scrolling functionality on main api index page not working
- Error when searching for subdivision names that have an accent on them e.g /Goiás,Paraíba,São Paulo, implemented unidecode library
- Error when searching for subdivision names that are named the same, all of the subdivisions should be returned not just the first one e.g Saint George, Saint Patrick, Bolivar, Sucre, saint andrew etc. 
- Spell check of code 
- For filter query string param, passing in no value to it would throw an error, now it just returns all data as is
- Error message path would only show the base url, excluding any query string params
- The filter query string parameter appended to the list_subdivisions endpoint was returning incorrect attributes, it's now ignored if it's appended
- Error when /name endpoint when no int/float value for likeness parameter is input, an error message should be returned rather than sever error
- Fixed issue with API execution being slow due to loading in the subdivision data each tine, solved by implementing LRU caching wrapper
- Fixed deprecated upload-artefact error in github workflow

## 1.5.4 - March 2024


### Added
- Query string parameter "likness" added for subdivision name endpoint that allows you to search for similarly named subdivisions using a 'likeness' score
- Copy icon/button that allows you to copy the example request url 


### Changed
- Links in API homepage should open in a separate tab
- Remove any GCP functionality, now using an instance of the iso3166-2 software itself for the data source
- Remove filter attribute


### Fixed
- When searching for a subdivision via its name, any name's that have an existing comma in them were being separated at the comma rather than handled as one name



## 1.4.0 - December 2023


### Added
- /alpha endpoint can now accept alpha-2, alpha-3 or numeric country code, can pass in multiple mismatched country codes
- Added description of each endpoint to top of on index.py 
- Filter attribute that allows you to filter out specific data attributes for each subdivision
- Added URL/path to output error message


### Changed
- Increased the % of likeness that a subdivision name has to be matched with the input, in difflib library 
- Subdivision code main the main key for each subdivision object rather than being encapsulated within the object
- /subd endpoint changed to /subdivision
- /name endpoint now used for subdivision name, /country_name used for country name
- More info on unit tests messages 
- Some endpoints will still be executed if '/api' is prepended or not to it


### Fixed
- Issue when passing in multiple subdivision names, only returning the first one
- Fixed issue with appending trailing slashes on endpoints, added app.url_map.strict_slashes = False
- Example links on API homepage not working


## v1.3.0 - December 2023


### Added
- Can search via subdivision name
- Table of contents on readme
- Attribute section on API homepage 
- Link in API homepage to list of supported countries
- API examples added to demo notebook


### Changed
- Make example links on API homepage clickable 


### Fixed
- Country names with spaces in them returning error


## <=v1.2.0 - September 2023

### Added 
- Initial API release
- Import ISO 3166-2 data from GCP backend