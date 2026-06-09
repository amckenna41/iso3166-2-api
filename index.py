from flask import Flask, request, render_template, jsonify, send_from_directory, Response
from urllib.parse import unquote_plus, unquote
from iso3166_2 import Subdivisions
import re
import os
import csv
import io
import json
import requests
from pycountry import countries, languages as pycountry_languages
from thefuzz import process
import random
from unidecode import unidecode
from functools import lru_cache
from math import radians, sin, cos, sqrt, atan2, ceil

########################################################### Endpoints ###########################################################
'''
/api - main homepage for API, displaying purpose, examples and documentation
/api/all - return all subdivision data for all countries
/api/alpha/<input_alpha> - return all subdivision data for input country using its ISO 3166-1 alpha-2, alpha-3 or numeric codes  
/api/subdivision/<input_subdivision> - return subdivision data for input subdivision using its subdivision code (GET)
/api/subdivision - bulk subdivision lookup via JSON body with a list of subdivision codes (POST)
/api/country_name/<input_country_name> - return all subdivision data for input country using its country name                        
/api/search/<input_search_term> - return all subdivision data for input subdivision name or search term    
/api/list_subdivisions/<input_alpha_code> - return all subdivision codes for ALL or a subset of countries
/api/coords - return subdivision data for input latitude and longitude coordinates
/api/random - return a random subdivision from the dataset
/api/stats - return statistics about the ISO 3166-2 dataset
/api/version - get current version of iso3166-2 package being used by the API (mainly for dev)
/api/clear-cache - clear the cached Subdivisions class instance and all cached subdivision data (mainly for dev)
/api/search_geo/<input_latlng> - search subdivision data by approximate lat/lng (latLng attribute)
'''
#################################################################################################################################


################################################### Query String Parameters ###################################################
'''
likeness (?likeness=N) - a value between 1 and 100 that increases or reduces the % of similarity/likeness that the inputted search
terms have to match to the subdivision data in the subdivision code, name and local/other name attributes. This can be used with the
/api/search and /api/country_name endpoints. Having a higher value returns more exact and fewer total matches; a lower value returns
less exact but more total matches, e.g /api/search/Paris?likeness=50, /api/country_name/Tajikist?likeness=90 (default=100).
Note: if using the iso3166-2 Python package directly, the equivalent function parameter is named likeness_score (not likeness).
filterAttributes (?filter=...) - a comma-separated list of attributes to include in the output. By default all attributes are 
returned. This parameter is supported by /api/all, /api/alpha, /api/subdivision, /api/search and /api/country_name, e.g 
/api/all?filter=name,latLng, api/alpha/DEU?filter=latLng,flag, api/subdivision/PL-02?filter=localOtherName.
excludeMatchScore - this allows you to exclude the matchScore attribute from the search results when using the /api/search endpoint. 
The match score is the % of a match each returned subdivision data object is to the search terms, with 100% being an exact match. By 
default the match score is returned for each object, e.g /api/search/Bucharest?excludeMatchScore=1, 
/api/search/Oregon?excludeMatchScore=1 (default=0).
format (?format=json|csv|geojson) - output format for the response. Default is json. csv returns a downloadable CSV file with one 
row per subdivision. geojson returns a GeoJSON FeatureCollection (lat/lng stored as Point geometry). Supported on /api/all, 
/api/alpha, /api/subdivision, /api/search and /api/country_name.
lang (?lang=<ISO639code>) - filter the localOtherName attribute to only include entries in the specified ISO 639 language, e.g 
/api/all?lang=fra, /api/alpha/DE?lang=deu. Supported on all data endpoints.
page (?page=N) - page number for paginated /api/all responses (1-indexed, default=1). Only active when ?page or ?pageSize is set.
pageSize (?pageSize=N) - number of countries per page for paginated /api/all responses (1-250, default=50).
'''
###############################################################################################################################

#initialise Flask app
app = Flask(__name__)

#register routes/endpoints with or without trailing slash
app.url_map.strict_slashes = False

#list of supported attributes
all_attributes = ["name", "localOtherName", "type", "parentCode", "flag", "latLng", "history"]

#token required to call /clear-cache (set via CACHE_CLEAR_TOKEN environment variable)
CACHE_CLEAR_TOKEN = os.environ.get("CACHE_CLEAR_TOKEN", "")

#country names that contain a comma and must not be split when parsing comma-separated country name input
NAME_COMMA_EXCEPTIONS = [
    "BOLIVIA, PLURINATIONAL STATE OF",
    "BONAIRE, SINT EUSTATIUS AND SABA",
    "CONGO, DEMOCRATIC REPUBLIC OF THE",
    "IRAN, ISLAMIC REPUBLIC OF",
    "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
    "KOREA, REPUBLIC OF",
    "MICRONESIA, FEDERATED STATES OF",
    "MOLDOVA, REPUBLIC OF",
    "PALESTINE, STATE OF",
    "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA",
    "TAIWAN, PROVINCE OF CHINA",
    "TANZANIA, UNITED REPUBLIC OF",
    "VIRGIN ISLANDS, BRITISH",
    "VIRGIN ISLANDS, U.S.",
    "VENEZUELA, BOLIVARIAN REPUBLIC OF"]

#common English aliases mapped to their official ISO 3166-1 country name
NAME_CONVERTED = {
    "UAE": "United Arab Emirates", "Brunei": "Brunei Darussalam", "Bolivia": "Bolivia, Plurinational State of",
    "Bosnia": "Bosnia and Herzegovina", "Bonaire": "Bonaire, Sint Eustatius and Saba", "DR Congo":
    "Congo, the Democratic Republic of the", "Ivory Coast": "Côte d'Ivoire", "Cape Verde": "Cabo Verde",
    "Cocos Islands": "Cocos (Keeling) Islands", "Falkland Islands": "Falkland Islands (Malvinas)",
    "Micronesia": "Micronesia, Federated States of", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
    "South Georgia": "South Georgia and the South Sandwich Islands", "Iran": "Iran, Islamic Republic of",
    "North Korea": "Korea, Democratic People's Republic of", "South Korea": "Korea, Republic of",
    "Laos": "Lao People's Democratic Republic", "Moldova": "Moldova, Republic of", "Saint Martin": "Saint Martin (French part)",
    "Macau": "Macao", "Pitcairn Islands": "Pitcairn", "Heard Island": "Heard Island and McDonald Islands",
    "Palestine": "Palestine, State of", "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha",
    "St Helena": "Saint Helena, Ascension and Tristan da Cunha", "Saint Kitts": "Saint Kitts and Nevis",
    "St Kitts": "Saint Kitts and Nevis", "St Vincent": "Saint Vincent and the Grenadines",
    "St Lucia": "Saint Lucia", "Saint Vincent": "Saint Vincent and the Grenadines", "Russia": "Russian Federation",
    "Sao Tome and Principe": "São Tomé and Príncipe", "Sint Maarten": "Sint Maarten (Dutch part)", "Syria": "Syrian Arab Republic",
    "Svalbard": "Svalbard and Jan Mayen", "French Southern and Antarctic Lands": "French Southern Territories", "Turkey": "Türkiye",
    "Taiwan": "Taiwan, Province of China", "Tanzania": "Tanzania, United Republic of", "USA": "United States of America",
    "United States": "United States of America", "Vatican City": "Holy See", "Vatican": "Holy See", "Venezuela":
    "Venezuela, Bolivarian Republic of", "Virgin Islands, British": "British Virgin Islands"}

@lru_cache()
def get_subdivision_instance():
    """ Cache function for initialization of Subdivisions instance. """
    return Subdivisions()

@lru_cache()
def get_all_subdivisions():
    """ Cache function for all data variable of Subdivisions instance. """
    return get_subdivision_instance().all

@lru_cache()
def get_alpha2_codes() -> set[str]:
    """ Cache function for list of valid ISO 3166-1 alpha-2 country codes. """
    return {c.alpha_2 for c in countries if hasattr(c, "alpha_2")}

@lru_cache()
def get_all_subdivision_codes() -> set[str]:
    """ Cache function for a flat set of all subdivision codes across every country. """
    codes = set()
    all_subs = get_all_subdivisions()
    for country in all_subs:
        codes.update(all_subs[country].keys())
    return codes

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """ Compute the great-circle distance in km between two lat/lng coordinate pairs. """
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c

@app.after_request
def add_cache_control(response):
    #add public Cache-Control for successful GET responses returning JSON data
    if request.method == 'GET' and response.status_code == 200 and 'application/json' in response.content_type:
        response.cache_control.public = True
        response.cache_control.max_age = 3600
    return response

@app.route('/')
@app.route('/api')
def home() -> str:
    """
    Default route for https://iso3166-2-api.vercel.app/. Main homepage for API displaying the 
    purpose of API and its documentation. 

    Parameters
    ==========
    None

    Returns
    =======
    :flask.render_template: html
      Flask html template for index.html page.
    """
    return render_template('index.html')

@app.route('/api/all', methods=['GET'])
@app.route('/all', methods=['GET'])
def all() -> tuple[dict, int]:
    """
    Flask route for '/api/all' path/endpoint. Return all ISO 3166-2 subdivision data 
    attributes and values for all countries. You can filter the attributes returned 
    using the 'filter' query string parameter and limit the number of countries 
    returned using the 'limit' query string parameter.

    Parameters
    ==========
    None

    Returns
    =======
    :jsonify(all_iso3166_2): json
        jsonified ISO 3166-2 subdivision data.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """  
    #parse filter query string param
    filter_param = request.args.get('filter')

    #parse limit parameter
    limit_param = request.args.get('limit')

    #get cached subdivision data
    all_iso3166_2_ = get_all_subdivisions()

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        all_iso3166_2_ = filter_attributes(filter_param, get_all_subdivisions())
        if (all_iso3166_2_ == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400   

    #limit number of countries returned, if applicable due to large amount of country data
    if not (limit_param is None):
        try:
            limit_param = int(limit_param)
        except ValueError:
            return jsonify(create_error_message("Limit query string parameter must be an integer.", request.url)), 400 

        if (limit_param < 1):
            return jsonify(create_error_message("Limit query string parameter must be greater than 0.", request.url)), 400 

        #slice the dict to only return the number of countries specified in limit param
        all_iso3166_2_ = dict(list(all_iso3166_2_.items())[:limit_param])

    #parse lang query string param and filter localOtherName to the requested language
    lang_param = request.args.get('lang')
    if lang_param:
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message("lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).", request.url)), 400
        all_iso3166_2_ = filter_lang_local_name(all_iso3166_2_, lang_param)

    #parse format query string param
    format_param = request.args.get('format', 'json').lower().strip()
    if format_param not in ('json', 'csv', 'geojson'):
        return jsonify(create_error_message(f"Unsupported format '{format_param}'. Supported formats: json, csv, geojson.", request.url)), 400

    #return non-JSON format if requested (bypasses pagination)
    if format_param != 'json':
        return make_format_response(all_iso3166_2_, format_param)

    #parse pagination params — only active when page or pageSize is explicitly provided
    page_param = request.args.get('page')
    page_size_param = request.args.get('pageSize')
    if page_param is not None or page_size_param is not None:
        try:
            page = int(page_param or 1)
            page_size = int(page_size_param or 50)
        except ValueError:
            return jsonify(create_error_message("page and pageSize query string parameters must be integers.", request.url)), 400
        if page < 1:
            return jsonify(create_error_message("page must be greater than 0.", request.url)), 400
        if not (1 <= page_size <= 250):
            return jsonify(create_error_message("pageSize must be between 1 and 250.", request.url)), 400
        all_keys = list(all_iso3166_2_.keys())
        total_countries = len(all_keys)
        total_pages = ceil(total_countries / page_size)
        start = (page - 1) * page_size
        page_data = {k: all_iso3166_2_[k] for k in all_keys[start:start + page_size]}
        return jsonify({
            "data": page_data,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages,
            "totalCountries": total_countries
        }), 200

    return jsonify(all_iso3166_2_), 200

@app.route('/alpha', methods=['GET'])
@app.route('/api/alpha', methods=['GET'])
@app.route('/api/alpha/<input_alpha>', methods=['GET'])
@app.route('/alpha/<input_alpha>', methods=['GET'])
def api_alpha(input_alpha: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/alpha' path/endpoint. Return all ISO 3166-2 subdivision data for the 
    country with the inputted ISO 3166-1 alpha-2, alpha-3 or numeric code/codes. If invalid alpha 
    code or no value input then return error.

    Parameters
    ==========
    :alpha: str/list (default="")
        2 letter alpha-2, 3 letter alpha-3 or numeric ISO 3166-1 country codes or list of codes. If 
        default value then return error.

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data per input alpha code. 
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise object to store output
    iso3166_2 = {}

    #if no input alpha parameter then return error message
    if (input_alpha == ""):
        return jsonify(create_error_message("The ISO 3166-1 alpha input parameter cannot be empty. Please pass in at least one alpha country code.", request.url)), 400    
    
    #remove unicode spacing from input alpha code if applicable
    input_alpha = input_alpha.replace("%20", '')

    #get the country subdivision data using the input alpha codes from the Subdivisions class, return error if invalid codes input
    try:
        iso3166_2 = get_subdivision_instance()[input_alpha]
    except ValueError as ve:
        error_msg = str(ve)
        if '. Did you mean' in error_msg:
            error_msg = error_msg[:error_msg.index('. Did you mean')] + '.'
        return jsonify(create_error_message(error_msg, request.url)), 400

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400

    #detect if data is flat {subdiv_code: data} (single country) or nested {country_code: {subdiv_code: data}} (multi-country)
    #single-country results have subdivision codes (containing '-') as top-level keys; multi-country results have alpha-2 codes
    first_key = next(iter(iso3166_2), None)
    is_flat = bool(first_key and '-' in first_key)
    if is_flat:
        country_alpha2 = first_key.split('-')[0]
        iso3166_2_nested = {country_alpha2: dict(iso3166_2)}
    else:
        iso3166_2_nested = dict(iso3166_2)

    #parse lang query string param and filter localOtherName to the requested language
    lang_param = request.args.get('lang')
    if lang_param:
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message("lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).", request.url)), 400
        if not (pycountry_languages.get(alpha_3=lang_param.lower()) or pycountry_languages.get(alpha_2=lang_param.lower())):
            return jsonify(create_error_message(f"Unrecognized ISO 639 language code: {lang_param}.", request.url)), 400
        iso3166_2_nested = filter_lang_local_name(iso3166_2_nested, lang_param)

    #parse format query string param
    format_param = request.args.get('format', 'json').lower().strip()
    if format_param not in ('json', 'csv', 'geojson'):
        return jsonify(create_error_message(f"Unsupported format '{format_param}'. Supported formats: json, csv, geojson.", request.url)), 400
    if format_param != 'json':
        return make_format_response(iso3166_2_nested, format_param)

    #unwrap back to flat format for single-country JSON responses
    if is_flat:
        return jsonify(iso3166_2_nested[country_alpha2]), 200
    return jsonify(iso3166_2_nested), 200

@app.route('/api/subdivision/<input_subdivision>', methods=['GET'])
@app.route('/subdivision/<input_subdivision>', methods=['GET'])
@app.route('/api/subdivision', methods=['GET'])
@app.route('/subdivision', methods=['GET'])
def api_subdivision(input_subdivision="") -> tuple[dict, int]:    
    """
    Flask route for '/api/subdivision' path/endpoint. Return all ISO 3166-2 subdivision data 
    for the inputted subdivision, according to its ISO 3166-2 code. A comma separated list of 
    subdivision codes can also be input. If invalid subdivision code or no value input then 
    return error.

    Parameters
    ==========
    :input_subdivision: str (default="")
        ISO 3166-2 subdivision code or list of codes.

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data per input subdivision code.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input.
    """
    #initialise vars
    iso3166_2 = {}
    subdivision_code = []

    #get flat set of all available subdivision codes from the cached dataset
    all_iso3166_2_codes = get_all_subdivision_codes()

    #if no input subdivision parameter then return error message
    if (input_subdivision == ""):
        return jsonify(create_error_message("The Subdivision input parameter cannot be empty. Please pass in at least one subdivision code.", request.url)), 400    
            
    #sort and uppercase all subdivision codes, remove any unicode spaces (%20)
    subdivision_code = sorted([input_subdivision.upper().replace(' ','').replace('%20', '')])
    
    #if first element in subdivision list is comma separated list of codes, split into actual array of comma separated codes
    if (',' in subdivision_code[0]):
        subdivision_code = subdivision_code[0].split(',')
        subdivision_code = [code.strip() for code in subdivision_code]

    #iterate over each subdivision code and validate its format and check if exists in dataset, if not then return error
    for subd in subdivision_code:
        #return error if input subdivision not in correct format
        if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", subd):
            return jsonify(create_error_message(f"All subdivision codes must be in the format XX-Y, XX-YY or XX-YYY, got {subd}.", request.url)), 400
        
        #return error if invalid subdivision input
        if subd not in all_iso3166_2_codes:
            return jsonify(create_error_message(f"Subdivision code {subd} not found in list of available subdivisions for {subd.split('-')[0]}.", request.url)), 400

        #add country code as parent key for nested subdivision objects
        cc = subd.split('-')[0]
        iso3166_2.setdefault(cc, {})[subd] = get_all_subdivisions()[cc][subd]

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400

    #parse lang query string param and filter localOtherName to the requested language
    lang_param = request.args.get('lang')
    if lang_param:
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message("lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).", request.url)), 400
        iso3166_2 = filter_lang_local_name(iso3166_2, lang_param)

    #parse format query string param
    format_param = request.args.get('format', 'json').lower().strip()
    if format_param not in ('json', 'csv', 'geojson'):
        return jsonify(create_error_message(f"Unsupported format '{format_param}'. Supported formats: json, csv, geojson.", request.url)), 400
    if format_param != 'json':
        return make_format_response(iso3166_2, format_param)

    return jsonify(iso3166_2), 200

@app.route('/api/search/<input_search_term>', methods=['GET'])
@app.route('/search/<input_search_term>', methods=['GET'])
@app.route('/api/search', methods=['GET'])
@app.route('/search', methods=['GET'])
def api_search(input_search_term: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/search' path/endpoint. Return all ISO 3166-2 subdivision data attributes and 
    values for inputted subdivision name/names or search terms. When searching for the sought subdivision,
    a fuzzy search algorithm is used via "thefuzz" package that finds the exact match within the 
    dataset, if this returns nothing then the dataset is searched for subdivision names that match 
    90% or more, the first match will then be returned. The value for this search parameter can be 
    changed via the 'likeness' query string parameter, which outlines the percentage likeness the 
    subdivision parameters have to be to the input search terms, decreasing the likeness will increase
    the search space. If no matching subdivision name found or input is empty then return an error. 

    By default, the Match Score attribute will be returned but not included for each search results, 
    which represents the % match that the search results are to the input search terms. If you want 
    to include this attribute from the search results then set the query string parameter 
    excludeMatchScore to 0.

    Parameters
    ==========
    :input_search_term: str/list (default="")
        one or more sought search terms.

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data per input subdivision name.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """
    #if no input parameters set then return error message
    if (input_search_term == ""):
        return jsonify(create_error_message("The search input parameter cannot be empty. Please pass in at least one search term.", request.url)), 400 
    
    #remove all whitespace & unicode characters
    search_terms = unquote(input_search_term).replace("%20", ' ')
    
    #parse likeness query string param, used as a % cutoff for likeness of subdivision names, raise error if invalid type or value input
    try:
        search_likeness_score = int(request.args.get('likeness', default="100").rstrip('/'))
    except ValueError:
        return jsonify(create_error_message("Likeness query string parameter must be an integer between 0 and 100.", request.url)), 400 

    #raise error if likeness score isn't between 0 and 100
    if not (0 <= search_likeness_score <= 100):
        return jsonify(create_error_message("Likeness query string parameter value must be between 0 and 100.", request.url)), 400 

    #parse query string parameter that allows user to include the Matching % score from search results, by default it is excluded in results
    exclude_match_score = (request.args.get('excludeMatchScore') or request.args.get('excludematchscore') or "true").lower().rstrip('/') in ['true', '1', 'yes']

    #call search function in iso3166-updates package, passing in likeness score & excludeMatchScore parameters, by default also search over the localOtherName attribute
    search_results = get_subdivision_instance().search(search_terms, likeness_score=search_likeness_score, exclude_match_score=exclude_match_score, local_other_name_search=True)

    #return message that no search results were found
    if not search_results:
        return jsonify({"Message": f"No matching subdivision data found with the given search term(s): {search_terms}. Try using the query string parameter '?likeness' and reduce the likeness score to expand the search space, '?likeness=30' will return subdivision data that have a 30% match to the input name. The current likeness score is set to {search_likeness_score}."}), 200

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        filtered_subdivisions = filter_attributes(filter_param, search_results, exclude_match_score)
        if (filtered_subdivisions == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the following list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400 
        
        #set filtered attributes object to that of the returned search results
        search_results = filtered_subdivisions

    #parse lang query string param — only applies when results are in nested dict format (excludeMatchScore=True)
    lang_param = request.args.get('lang')
    if lang_param and isinstance(search_results, dict):
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message("lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).", request.url)), 400
        search_results = filter_lang_local_name(search_results, lang_param)

    #parse format query string param — only applies for nested dict format
    if isinstance(search_results, dict):
        format_param = request.args.get('format', 'json').lower().strip()
        if format_param not in ('json', 'csv', 'geojson'):
            return jsonify(create_error_message(f"Unsupported format '{format_param}'. Supported formats: json, csv, geojson.", request.url)), 400
        if format_param != 'json':
            return make_format_response(search_results, format_param)

    return jsonify(search_results), 200

@app.route('/api/search_geo/<input_latlng>', methods=['GET'])
@app.route('/search_geo/<input_latlng>', methods=['GET'])
@app.route('/api/search_geo', methods=['GET'])
@app.route('/search_geo', methods=['GET'])
def api_search_geo(input_latlng: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/search_geo' path/endpoint. Return ISO 3166-2 subdivision data
    for subdivisions whose latLng attribute is approximately equal to the input latitude
    and longitude. The input is a comma separated string of "lat,lng".

    Parameters
    ==========
    :input_latlng: str (default="")
        comma separated latitude and longitude, e.g. "39.4178,-2.6232".

    Query Parameters
    =================
    :radius: float (default=50)
        search radius in kilometers for approximate matching.

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data for matched subdivisions.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an
        invalid parameter input.
    """
    #if no input parameters set then return error message
    if (input_latlng == ""):
        return jsonify(create_error_message("The search_geo input parameter cannot be empty. Please pass in a comma separated lat,lng string.", request.url)), 400

    #parse radius query string param (km)
    try:
        radius_km = float(request.args.get('radius', default="50").rstrip('/'))
    except ValueError:
        return jsonify(create_error_message("Radius query string parameter must be a number greater than 0.", request.url)), 400

    if (radius_km <= 0):
        return jsonify(create_error_message("Radius query string parameter must be greater than 0.", request.url)), 400

    #remove whitespace/unicode and split into lat/lng
    latlng_parts = unquote(input_latlng).replace('%20', '').split(',')
    if len(latlng_parts) != 2:
        return jsonify(create_error_message("Input latlng must be a comma separated string of latitude and longitude, e.g. '39.4178,-2.6232'.", request.url)), 400

    #validate and parse lat/lng
    try:
        latitude = float(latlng_parts[0])
        longitude = float(latlng_parts[1])
    except ValueError:
        return jsonify(create_error_message("Latitude and longitude must be valid numbers.", request.url)), 400

    if not (-90 <= latitude <= 90):
        return jsonify(create_error_message(f"Latitude value {latitude} is out of range. Latitude must be between -90 and 90.", request.url)), 400
    if not (-180 <= longitude <= 180):
        return jsonify(create_error_message(f"Longitude value {longitude} is out of range. Longitude must be between -180 and 180.", request.url)), 400

    #search all subdivisions for approximate lat/lng matches
    all_iso3166_2 = get_all_subdivisions()
    matched_subdivisions = {}

    for country_code, subdivisions in all_iso3166_2.items():
        for subdivision_code, subdivision_data in subdivisions.items():
            latlng = subdivision_data.get('latLng')
            if not latlng or len(latlng) != 2:
                continue

            subd_lat, subd_lng = latlng[0], latlng[1]
            distance_km = haversine_km(latitude, longitude, subd_lat, subd_lng)

            if distance_km <= radius_km:
                matched_subdivisions.setdefault(country_code, {})[subdivision_code] = subdivision_data

    if not matched_subdivisions:
        return jsonify({"Message": f"No matching subdivision data found within {radius_km} km of lat={latitude}, lng={longitude}. Try increasing the radius using '?radius=100'."}), 200

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable
    if not (filter_param is None):
        filtered_subdivisions = filter_attributes(filter_param, matched_subdivisions)
        if (filtered_subdivisions == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400

        matched_subdivisions = filtered_subdivisions

    return jsonify(matched_subdivisions), 200

@app.route('/api/country_name/<input_country_name>', methods=['GET'])
@app.route('/country_name/<input_country_name>', methods=['GET'])
@app.route('/api/country_name', methods=['GET'])
@app.route('/country_name', methods=['GET'])
def api_country_name(input_country_name="") -> tuple[dict, int]:
    """
    Flask route for '/api/country_name' path/endpoint. Return all ISO 3166-2 subdivision data attributes and 
    values for inputted country name/names. A closeness function is used on the input country name 
    to get the closest match, to a high degree, from the list of available countries, e.g if Swede 
    is input then the data for Sweden will be returned. Return error if invalid country name or no name 
    parameter input. 

    Parameters
    ==========
    :input_country_name: str/list (default="")
        one or more country names as they are commonly known in English. 

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data per input country name.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """
    #initialise vars
    iso3166_2 = {}
    alpha2_code = []
    names = []

    #decode any unicode or accent characters using utf-8 encoding, lower case and remove additional whitespace
    name = unidecode(unquote_plus(input_country_name)).replace('%20', ' ').title()

    #if no input parameters set then return error message
    if (name == ""):
        return jsonify(create_error_message("The country name input parameter cannot be empty. Please pass in at least one country name.", request.url)), 400   

    #check if input country is in the exceptions list; if not, split on comma into a sorted list
    if (name.upper() in NAME_COMMA_EXCEPTIONS):
        names = [name]
    else:
        names = sorted(name.split(','))

    #convert country names using module-level alias map, if applicable
    for name_ in range(0, len(names)):
        if names[name_].title() in NAME_CONVERTED:
            names[name_] = NAME_CONVERTED[names[name_].title()]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from pycountry, remove whitespace
    all_names_no_space = [country.name.strip(' ') for country in countries]
    
    #iterate over all input country names, get corresponding 2 letter alpha-2 code
    for name_ in names:

        #using thefuzz library, get all countries that match the input country name
        all_country_name_matches = process.extract(name_.upper(), all_names_no_space)
        name_matches = []
        
        #iterate over all found country matches, look for exact matches, if none found then look for ones that have likeness score>=90
        for match in all_country_name_matches:
            #use default likeness score of 100 (exact) followed by 90 if no exact matches found
            if (match[1] == 100):
                name_matches.append(match[0])
                break
            elif (match[1] >= 90):
                name_matches.append(match[0])
                break
            else:
                #return error if country name not found
                return jsonify(create_error_message(f"Invalid country name input: {name}.", request.url)), 400             

        #use pycountry to find corresponding alpha-2 code from its name
        country_match = countries.get(name=name_matches[0])
        if country_match is None:
            return jsonify(create_error_message(f"Invalid country name input: {name}.", request.url)), 400
        alpha2_code.append(country_match.alpha_2)
    
    #get country data from ISO 3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_2[code] = get_all_subdivisions()[code]

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400             

    #parse lang query string param and filter localOtherName to the requested language
    lang_param = request.args.get('lang')
    if lang_param:
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message("lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).", request.url)), 400
        iso3166_2 = filter_lang_local_name(iso3166_2, lang_param)

    #parse format query string param
    format_param = request.args.get('format', 'json').lower().strip()
    if format_param not in ('json', 'csv', 'geojson'):
        return jsonify(create_error_message(f"Unsupported format '{format_param}'. Supported formats: json, csv, geojson.", request.url)), 400
    if format_param != 'json':
        return make_format_response(iso3166_2, format_param)

    return jsonify(iso3166_2), 200

@app.route('/api/list_subdivisions', methods=['GET'])
@app.route('/list_subdivisions', methods=['GET'])
@app.route('/api/list_subdivisions/<input_alpha>', methods=['GET'])
@app.route('/list_subdivisions/<input_alpha>', methods=['GET'])
def api_list_subdivisions(input_alpha: str="") -> tuple[dict, int]:
    """
    Flask route for '/api/list_subdivisions' path/endpoint. Return all ISO 3166 country codes and 
    a list of just their subdivision codes. A comma separated list of individual ISO 3166 country
    codes can also be input.
    
    Parameters
    ==========
    :input_alpha: str (default="")
        2 letter alpha-2, 3 letter alpha-3 or numeric ISO 3166-1 country codes or list of codes.

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 country codes and their subdivision codes.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input. 
    """
    iso3166_2 = {}

    #remove unicode spacing from input alpha code if applicable
    input_alpha = input_alpha.replace("%20", '')

    if (input_alpha == ""):
        #iterate through each country code, append its subdivisions to export object
        for country in get_all_subdivisions():
            iso3166_2[country] = []
            for subdivision in get_all_subdivisions()[country]:
                iso3166_2[country].append(subdivision)
    else:
        #get the country subdivision data using the input alpha codes, return error if invalid codes input
        try:
            iso3166_2 = get_subdivision_instance().subdivision_codes(input_alpha)
        except ValueError as ve:
            return jsonify(create_error_message(str(ve), request.url)), 400   

    return jsonify(iso3166_2), 200

@app.errorhandler(404)
def not_found(e) -> tuple[dict, int]:
    """
    Return html template for 404.html when page/path not found in Flask app.

    Parameters
    ==========
    :e: int
        error code.

    Returns
    =======
    :flask.render_template: html
      Flask html template for 404.html page.
    :status_code: int
        response status code. 404 code implies page not found.
    """
    #validation in the case of user inputting /alpha2, /alpha3 or /numeric endpoint instead of /alpha
    if any(alpha in request.url for alpha in ["alpha2", "alpha3", "numeric"]):
        return render_template("404.html", path=request.url, 
            alpha_endpoint_message="Searching using a country's alpha code (alpha-2, alpha-3 or numeric code) should use the /alpha endpoint."), 404

    #validation in the case of user inputting /subdivision_name endpoint instead of /name
    if any(alpha in request.url for alpha in ["subdivision_name"]):
        return render_template("404.html", path=request.url, 
            alpha_endpoint_message="Searching using a country's subdivision name should use the /name endpoint."), 404
    
    return render_template("404.html", path=request.url), 404
    
def filter_attributes(filter_list: str, filtered_iso3166_2: dict, exclude_match_score: bool=1) -> dict|int:
    """
    Filter out attributes in ISO 3166-2 subdivision dataset not listed in filter 
    query string parameter. Validate each attribute input to the query string. 

    Parameters
    ==========
    :filter_list: str
        list of attributes to include for each subdivision.
    :filtered_iso3166_2: dict
        object of subdivision data to be filtered per attribute.
    :exclude_match_score: bool (default=1)
        exclude the % match score from the output.

    Returns
    =======
    :filtered_iso3166_2/-1: dict/int
        object of filtered subdivision data. If no attribute value input then the 
        same object data is returned. Or -1 if in an invalid attribute is input to 
        query parameter. 
    """
    #split attributes into comma separated list, remove any whitespace
    filter_list = filter_list.replace(' ', '').split(',')

    #temp var for editing list
    temp_filter = filter_list
    
    #iterate over each attribute in filtered list, return error if invalid attribute input
    for attr in filter_list:
        #return all attributes if wildcard symbol input
        if (attr == "*"):
            temp_filter = all_attributes
            break 
        if (not attr in all_attributes and attr != ''):
            return -1
    
    filter_list = temp_filter

    #recursive function that recursively removes any unwanted attributes per subdivision object
    def filter_dict(d, attributes_to_keep):
        if isinstance(d, dict):
            return {k: filter_dict(v, attributes_to_keep) for k, v in d.items() if k in attributes_to_keep or isinstance(v, dict)}
        elif isinstance(d, list):
            return [filter_dict(i, attributes_to_keep) for i in d]
        else:
            return d
    
    #if the Match score and its attributes are to be included in output, add them to filter list
    if not (exclude_match_score):
        filter_list.extend(["matchScore", "countryCode", "subdivisionCode"])

    #return all data as is if no filter value input
    if (filter_list != ['']):
        #keep only the specified attributes 
        filtered_iso3166_2 = filter_dict(filtered_iso3166_2, set(filter_list))
    
    return filtered_iso3166_2

def create_error_message(message: str, path: str, status: int = 400) -> dict:
    """ Helper function that returns error message when one occurs in Flask app. """
    return {"message": message, "path": path, "status": status}

def filter_lang_local_name(data: dict, lang: str) -> dict:
    """
    Filter the localOtherName attribute in all subdivisions to only include entries whose
    language tag matches the given ISO 639 language code (case-insensitive).

    localOtherName entries are comma-separated strings in the form "Name (langcode)" or
    "'Name with, comma (langcode)'" for names that contain commas.

    Parameters
    ==========
    :data: dict
        nested {country_code: {subdiv_code: data}} object.
    :lang: str
        ISO 639 language code to filter by (e.g. "fra", "eng").

    Returns
    =======
    :result: dict
        a new nested dict with localOtherName filtered per subdivision.
    """
    entry_re = re.compile(
        r"'[^']*\(\s*" + re.escape(lang.strip()) + r"\s*\)'"
        r"|"
        r"[^,]*\(\s*" + re.escape(lang.strip()) + r"\s*\)",
        re.IGNORECASE
    )
    result = {}
    for country_code, subdivisions in data.items():
        result[country_code] = {}
        for subdiv_code, subdiv_data in subdivisions.items():
            new_data = dict(subdiv_data)
            local = new_data.get('localOtherName')
            if local:
                matches = entry_re.findall(local)
                new_data['localOtherName'] = ', '.join(m.strip().strip("'") for m in matches) if matches else None
            result[country_code][subdiv_code] = new_data
    return result

def make_format_response(data: dict, format_param: str) -> Response:
    """
    Convert the standard nested {country: {subdiv: data}} object to the requested
    output format and return an appropriate Flask Response.

    Parameters
    ==========
    :data: dict
        nested {country_code: {subdiv_code: data}} object.
    :format_param: str
        one of 'csv' or 'geojson'.

    Returns
    =======
    :flask.Response
        CSV or GeoJSON response.
    """
    if format_param == 'geojson':
        features = []
        for country_code, subdivisions in data.items():
            for subdiv_code, subdiv_data in subdivisions.items():
                latlng = subdiv_data.get('latLng')
                geometry = None
                if latlng and len(latlng) == 2:
                    geometry = {
                        "type": "Point",
                        "coordinates": [latlng[1], latlng[0]]  # GeoJSON order: [lng, lat]
                    }
                properties = {k: v for k, v in subdiv_data.items() if k != 'latLng'}
                properties['countryCode'] = country_code
                properties['subdivisionCode'] = subdiv_code
                features.append({
                    "type": "Feature",
                    "id": subdiv_code,
                    "geometry": geometry,
                    "properties": properties
                })
        geojson = {"type": "FeatureCollection", "features": features}
        return Response(json.dumps(geojson), status=200, mimetype='application/geo+json')

    if format_param == 'csv':
        fieldnames = ['subdivisionCode', 'countryCode', 'name', 'localOtherName',
                      'type', 'parentCode', 'latLng', 'flag', 'history']
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for country_code, subdivisions in data.items():
            for subdiv_code, subdiv_data in subdivisions.items():
                row = {
                    'subdivisionCode': subdiv_code,
                    'countryCode': country_code,
                    'name': subdiv_data.get('name') or '',
                    'localOtherName': subdiv_data.get('localOtherName') or '',
                    'type': subdiv_data.get('type') or '',
                    'parentCode': subdiv_data.get('parentCode') or '',
                    'latLng': str(subdiv_data.get('latLng')) if subdiv_data.get('latLng') else '',
                    'flag': subdiv_data.get('flag') or '',
                    'history': json.dumps(subdiv_data.get('history')) if subdiv_data.get('history') else ''
                }
                writer.writerow(row)
        return Response(
            output.getvalue(),
            status=200,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename="iso3166-2.csv"'}
        )

@app.route('/clear-cache')
@app.route('/api/clear-cache')
def clear_cache():
    """ Clear cache of Subdivisions class instance and all cached subdivision data. Requires valid CACHE_CLEAR_TOKEN. """
    token = request.args.get('token', '')
    if not CACHE_CLEAR_TOKEN or token != CACHE_CLEAR_TOKEN:
        return jsonify(create_error_message("Unauthorized. A valid token query parameter is required.", request.url, 401)), 401
    get_subdivision_instance.cache_clear()
    get_all_subdivisions.cache_clear()
    get_all_subdivision_codes.cache_clear()
    return 'Cache cleared'

@app.route('/version')
@app.route('/api/version')
def get_version():
    """ Get the current version of the iso3166-2 being used by the API. Mainly used for dev. """
    return get_subdivision_instance().__version__

@app.route('/api/stats', methods=['GET'])
@app.route('/stats', methods=['GET'])
def api_stats() -> tuple[dict, int]:
    """
    Flask route for '/api/stats' path/endpoint. Return live statistics about the ISO 3166-2
    dataset: total countries, total subdivisions, flag coverage, etc.

    Parameters
    ==========
    None

    Returns
    =======
    :jsonify(stats): json
        jsonified statistics object.
    :status_code: int
        response status code. 200 is a successful response.
    """
    all_data = get_all_subdivisions()

    total_countries = len(all_data)
    subdivision_counts = {c: len(all_data[c]) for c in all_data}
    countries_with_subdivisions = sum(1 for c in subdivision_counts if subdivision_counts[c] > 0)
    total_subdivisions = sum(subdivision_counts.values())
    avg_per_country = round(total_subdivisions / countries_with_subdivisions, 2) if countries_with_subdivisions else 0

    nonzero = {c: n for c, n in subdivision_counts.items() if n > 0}
    max_country = max(nonzero, key=nonzero.get) if nonzero else None
    min_country = min(nonzero, key=nonzero.get) if nonzero else None

    total_with_flags = sum(
        1 for c in all_data for s in all_data[c] if all_data[c][s].get('flag')
    )
    flag_pct = round(total_with_flags / total_subdivisions * 100, 1) if total_subdivisions else 0

    return jsonify({
        "totalCountries": total_countries,
        "totalSubdivisions": total_subdivisions,
        "countriesWithSubdivisions": countries_with_subdivisions,
        "countriesWithoutSubdivisions": total_countries - countries_with_subdivisions,
        "averageSubdivisionsPerCountry": avg_per_country,
        "maxSubdivisions": {"country": max_country, "count": nonzero.get(max_country, 0)} if max_country else None,
        "minSubdivisions": {"country": min_country, "count": nonzero.get(min_country, 0)} if min_country else None,
        "flagCoverage": {"count": total_with_flags, "percentage": flag_pct},
        "packageVersion": get_subdivision_instance().__version__
    }), 200

@app.route('/api/subdivision', methods=['POST'])
@app.route('/subdivision', methods=['POST'])
def api_subdivision_post() -> tuple[dict, int]:
    """
    Flask route for POST '/api/subdivision'. Bulk subdivision lookup via a JSON request body.
    Accepts a 'codes' field containing a list of ISO 3166-2 subdivision codes (max 500).
    Equivalent to the GET endpoint but suited for large payloads that exceed URL length limits.

    Request body
    ============
    {
        "codes": ["GB-ABD", "FR-75", "US-CA", ...]
    }

    Returns
    =======
    :jsonify(iso3166_2): json
        jsonified ISO 3166-2 subdivision data keyed by country then subdivision code.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an
        invalid parameter input.
    """
    body = request.get_json(silent=True)
    if not body or 'codes' not in body:
        return jsonify(create_error_message(
            "Request body must be valid JSON with a 'codes' field containing a list of subdivision codes.",
            request.url)), 400

    codes = body['codes']
    if not isinstance(codes, list) or len(codes) == 0:
        return jsonify(create_error_message(
            "'codes' must be a non-empty list of subdivision codes.", request.url)), 400

    if len(codes) > 500:
        return jsonify(create_error_message(
            "A maximum of 500 subdivision codes can be submitted per request.", request.url)), 400

    all_iso3166_2_codes = get_all_subdivision_codes()
    iso3166_2 = {}

    for subd in codes:
        if not isinstance(subd, str):
            return jsonify(create_error_message(
                f"All codes must be strings, got {type(subd).__name__}.", request.url)), 400
        subd = subd.upper().strip()
        if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", subd):
            return jsonify(create_error_message(
                f"All subdivision codes must be in the format XX-Y, XX-YY or XX-YYY, got {subd}.",
                request.url)), 400
        if subd not in all_iso3166_2_codes:
            return jsonify(create_error_message(
                f"Subdivision code {subd} not found in list of available subdivisions for {subd.split('-')[0]}.",
                request.url)), 400
        cc = subd.split('-')[0]
        iso3166_2.setdefault(cc, {})[subd] = get_all_subdivisions()[cc][subd]

    filter_param = request.args.get('filter')
    if filter_param is not None:
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if iso3166_2 == -1:
            return jsonify(create_error_message(
                f'Invalid attribute name input to filter query string parameter: {filter_param}. '
                f'Refer to the list of supported attributes: {", ".join(all_attributes)}.',
                request.url)), 400

    lang_param = request.args.get('lang')
    if lang_param:
        lang_param = lang_param.strip()
        if not re.match(r'^[a-zA-Z0-9]{2,10}$', lang_param):
            return jsonify(create_error_message(
                "lang query string parameter must be an ISO 639 language code (2–10 alphanumeric characters).",
                request.url)), 400
        iso3166_2 = filter_lang_local_name(iso3166_2, lang_param)

    return jsonify(iso3166_2), 200

@app.get("/openapi.yaml")
@app.get("/spec")
@app.get("/api/openapi.yaml")
@app.get("/api/spec")
def openapi_yaml():
    """ Serve the OpenAPI specification YAML file. """
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "openapi.yaml", mimetype="text/yaml")

@app.route('/api/coords', methods=['GET'])
@app.route('/coords', methods=['GET'])
def api_coords() -> tuple[dict, int]:
    """
    Flask route for '/api/coords' path/endpoint. Return ISO 3166-2 subdivision data for the 
    inputted latitude and longitude coordinates. Uses the OpenStreetMap Nominatim API to 
    reverse geocode the coordinates and retrieve the subdivision code.

    Parameters
    ==========
    lat: float (query parameter)
        latitude coordinate (-90 to 90).
    lng: float (query parameter)
        longitude coordinate (-180 to 180).

    Returns
    =======
    :iso3166_2: json
        jsonified response of iso3166-2 data for the subdivision at the given coordinates.
    :status_code: int
        response status code. 200 is a successful response, 400 means there was an 
        invalid parameter input, 404 means no subdivision found at coordinates.
    """
    #parse latitude and longitude from query parameters
    lat_param = request.args.get('lat')
    lng_param = request.args.get('lng')
    
    #validate that both parameters are provided
    if lat_param is None or lng_param is None:
        return jsonify(create_error_message("Both 'lat' and 'lng' query parameters are required. Example: /api/coords?lat=51.5074&lng=-0.1278", request.url)), 400
    
    #validate and parse latitude
    try:
        latitude = float(lat_param)
    except ValueError:
        return jsonify(create_error_message(f"Invalid latitude value: {lat_param}. Latitude must be a number between -90 and 90.", request.url)), 400
    
    #validate latitude range
    if not (-90 <= latitude <= 90):
        return jsonify(create_error_message(f"Latitude value {latitude} is out of range. Latitude must be between -90 and 90.", request.url)), 400
    
    #validate and parse longitude
    try:
        longitude = float(lng_param)
    except ValueError:
        return jsonify(create_error_message(f"Invalid longitude value: {lng_param}. Longitude must be a number between -180 and 180.", request.url)), 400
    
    #validate longitude range
    if not (-180 <= longitude <= 180):
        return jsonify(create_error_message(f"Longitude value {longitude} is out of range. Longitude must be between -180 and 180.", request.url)), 400
    
    #call OpenStreetMap Nominatim API for reverse geocoding
    nominatim_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=10&addressdetails=1"
    
    #set user agent header for OSM API (required by their usage policy)
    headers = {
        "User-Agent": "iso3166-2-api/1.0 (https://github.com/amckenna41/iso3166-2-api)"
    }
    
    try:
        osm_response = requests.get(nominatim_url, headers=headers, timeout=10)
        osm_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify(create_error_message(f"Error connecting to OpenStreetMap API: {str(e)}", request.url, 500)), 500
    
    osm_data = osm_response.json()
    
    #check if OSM returned an error or no results
    if 'error' in osm_data:
        return jsonify(create_error_message(f"No location found at coordinates lat={latitude}, lng={longitude}. The coordinates may be in an ocean or remote area.", request.url, 404)), 404
    
    #extract country code and subdivision code from OSM response
    address = osm_data.get('address', {})
    country_code = address.get('country_code', '').upper()
    
    if not country_code:
        return jsonify(create_error_message(f"Could not determine country from coordinates lat={latitude}, lng={longitude}.", request.url, 404)), 404
    
    #check if country code is valid
    if country_code not in get_alpha2_codes():
        return jsonify(create_error_message(f"Invalid or unsupported country code {country_code} returned from coordinates.", request.url, 404)), 404
    
    #try to extract subdivision code from OSM response
    #OSM uses ISO 3166-2 codes in some responses
    iso3166_2_code = osm_data.get('address', {}).get('ISO3166-2-lvl4', '')
    
    #if ISO3166-2-lvl4 not available, try to construct from state/province
    if not iso3166_2_code:
        #try different administrative level keys that OSM might return
        state_keys = ['state', 'province', 'region', 'county', 'state_district']
        state_name = None
        
        for key in state_keys:
            if key in address:
                state_name = address[key]
                break
        
        if not state_name:
            return jsonify(create_error_message(f"Could not determine subdivision from coordinates lat={latitude}, lng={longitude}. The location may not have subdivision data available.", request.url, 404)), 404
        
        #search for the subdivision by name within the country
        try:
            all_country_subdivisions = get_subdivision_instance()[country_code]
            
            #search through subdivisions to find matching name
            found_subdivision = None
            for subd_code, subd_data in all_country_subdivisions.items():
                if subd_data.get('name', '').lower() == state_name.lower():
                    found_subdivision = subd_code
                    break
                #also check localOtherName if available
                local_other_name = subd_data.get('localOtherName', '')
                if local_other_name and state_name.lower() in local_other_name.lower():
                    found_subdivision = subd_code
                    break
            
            if not found_subdivision:
                return jsonify(create_error_message(f"Could not find subdivision '{state_name}' in country {country_code}. The coordinates may be in an area without ISO 3166-2 subdivision data.", request.url, 404)), 404
            
            iso3166_2_code = found_subdivision
            
        except (ValueError, KeyError) as e:
            return jsonify(create_error_message(f"Error retrieving subdivision data for country {country_code}: {str(e)}", request.url, 404)), 404
    
    #validate the subdivision code format
    if not re.match(r"^[A-Z]{2}-[A-Z0-9]{1,3}$", iso3166_2_code):
        return jsonify(create_error_message(f"Invalid subdivision code format returned: {iso3166_2_code}.", request.url, 404)), 404
    
    #get the subdivision data
    try:
        all_iso3166_2 = get_all_subdivisions()
        
        if country_code not in all_iso3166_2:
            return jsonify(create_error_message(f"Country {country_code} not found in subdivision database.", request.url, 404)), 404
        
        if iso3166_2_code not in all_iso3166_2[country_code]:
            return jsonify(create_error_message(f"Subdivision code {iso3166_2_code} not found for country {country_code}.", request.url, 404)), 404
        
        subdivision_data = all_iso3166_2[country_code][iso3166_2_code]
        
        #structure output in standard format: {country_code: {subdivision_code: data}}
        iso3166_2 = {
            country_code: {iso3166_2_code: subdivision_data}
        }
        
        #parse filter query string param
        filter_param = request.args.get('filter')
        
        #filter out attributes from filter query parameter, if applicable
        if not (filter_param is None):
            iso3166_2 = filter_attributes(filter_param, iso3166_2)
            if (iso3166_2 == -1):
                return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400
        
        return jsonify(iso3166_2), 200
        
    except Exception as e:
        return jsonify(create_error_message(f"Error retrieving subdivision data: {str(e)}", request.url, 500)), 500

@app.route('/random')
@app.route('/api/random')
def get_random() -> tuple[dict, int]:
    """
    Flask route for '/api/random' path/endpoint. Return a random subdivision from the 
    ISO 3166-2 dataset, including all its attributes and values in the standard format.

    Parameters
    ==========
    None

    Returns
    =======
    :iso3166_2: json
        jsonified response containing the random subdivision data with subdivision code 
        as key and its attributes as values.
    :status_code: int
        response status code. 200 is a successful response.
    """
    #get all subdivision data from cache
    all_iso3166_2 = get_all_subdivisions()
    
    #collect all subdivision codes with their country codes
    all_subdivisions = []
    for country_code, subdivisions in all_iso3166_2.items():
        for subdivision_code in subdivisions.keys():
            all_subdivisions.append((country_code, subdivision_code))
    
    #select a random subdivision from all available subdivisions
    random_country_code, random_subdivision_code = random.choice(all_subdivisions)
    
    #get the subdivision data
    random_subdivision_data = all_iso3166_2[random_country_code][random_subdivision_code]
    
    #structure output in standard format: {country_code: {subdivision_code: data}}
    iso3166_2 = {
        random_country_code: {random_subdivision_code: random_subdivision_data}
    }
    
    #parse filter query string param
    filter_param = request.args.get('filter')
    
    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f'Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.', request.url)), 400
    
    return jsonify(iso3166_2), 200

# def handler(environ, start_response):
#     return app(environ, start_response)

if __name__ == '__main__':
    #run Flask app 
    app.run(debug=True)