# Change Log 

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