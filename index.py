from flask import Flask, request, render_template, jsonify
from urllib.parse import unquote_plus
import iso3166
from iso3166_2 import *
import re
from thefuzz import fuzz, process
from urllib.parse import unquote
from unidecode import unidecode
from functools import lru_cache

########################################################### Endpoints ###########################################################
'''
/api - main homepage for API, displaying purpose, examples and documentation
/api/all - return all subdivision data for all countries
/api/alpha/<input_alpha> - return all subdivision data for input country using its ISO 3166-1 alpha-2, alpha-3 or numeric codes  
/api/subdivision/<input_subdivision> - return subdivision data for input subdivision using its subdivision code             
/api/country_name/<input_country_name> - return all subdivision data for input country using its country name                        
/api/search/<input_search_term> - return all subdivision data for input subdivision name or search term    
/api/list_subdivisions/<input_alpha_code> - return all subdivision codes for ALL or a subset of countries
'''
#################################################################################################################################


################################################### Query String Parameters ###################################################
'''
likeness- this is a value between 1 and 100 that increases or reduces the % of similarity/likeness that the inputted search terms 
have to match to the subdivision data in the subdivision code, name and local/other name attributes. This can be used with the 
/api/search and /api_country_name endpoints. Having a higher value should return more exact and less total matches and having 
a lower value will return less exact but more total matches, e.g /api/search/Paris?likeness=50, 
/api/country_name/Tajikist?likeness=90 (default=100).
filterAttributes - this is a list of the default supported attributes that you want to include in the output. By default all attributes 
will be returned but this parameter is useful if you only require a subset of attributes, e.g api/alpha/DEU?filter=latLng,flag, 
api/subdivision/PL-02?filter=localOtherName.
excludeMatchScore - this allows you to exclude the matchScore attribute from the search results when using the /api/search endpoint. 
The match score is the % of a match each returned subdivision data object is to the search terms, with 100% being an exact match. By 
default the match score is returned for each object, e.g /api/search/Bucharest?excludeMatchScore=1, 
/api/search/Oregon?excludeMatchScore=1 (default=0).
'''
###############################################################################################################################

#initialise Flask app
app = Flask(__name__)

#register routes/endpoints with or without trailing slash
app.url_map.strict_slashes = False

#json object storing the error message, route and status code 
error_message = {}
error_message["status"] = 400

#list of supported attributes
all_attributes = ["name", "localOtherName", "type", "parentCode", "flag", "latLng", "history"]

@lru_cache()
def get_subdivision_instance():
    """ Cache function for initialization of Subdivisions instance. """
    return Subdivisions()

@lru_cache()
def get_all_subdivisions():
    """ Cache function for all data variable of Subdivisions instance. """
    return get_subdivision_instance().all

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
    attributes and values for all countries.

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

    #set path url for error message object
    error_message['path'] = request.url

    #get cached subdivision data
    all_iso3166_2_ = get_all_subdivisions()

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        all_iso3166_2_ = filter_attributes(filter_param, get_all_subdivisions())
        if (all_iso3166_2_ == -1):
            return jsonify(create_error_message(f"Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.", request.url)), 400   

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
        return jsonify(create_error_message("The ISO 3166-1 alpha input parameter cannot be empty.", request.url)), 400    
    
    #set path url for error message object
    error_message['path'] = request.url
    
    #remove unicode spacing from input alpha code if applicable
    input_alpha = input_alpha.replace("%20", '')

    #get the country subdivision data using the input alpha codes from the Subdivisions class, return error if invalid codes input
    try:
        iso3166_2 = get_subdivision_instance()[input_alpha]
    except ValueError as ve:
        return jsonify(create_error_message(str(ve), request.url)), 400   

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f"Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.", request.url)), 400   

    return jsonify(iso3166_2), 200

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

    #set path url for error message object
    error_message['path'] = request.url

    #get list of all available subdivision codes via the cached Subdivisions class instance
    all_iso3166_2_codes = []
    for country in get_all_subdivisions():
        for subdivision_code in get_all_subdivisions()[country]:
            all_iso3166_2_codes.append(subdivision_code)

    #if no input subdivision parameter then return error message
    if (input_subdivision == ""):
        return jsonify(create_error_message("The Subdivision input parameter cannot be empty.", request.url)), 400    
            
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
            return jsonify(create_error_message(f"Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.", request.url)), 400

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
        return jsonify(create_error_message("The search input parameter cannot be empty.", request.url)), 400 
    
    #remove all whitespace & unicode characters
    search_terms = unquote(input_search_term).replace("%20", '')
    
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
            return jsonify(create_error_message(f"Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the following list of supported attributes: {", ".join(all_attributes)}.", request.url)), 400 
        
        #set filtered attributes object to that of the returned search results
        search_results = filtered_subdivisions

    return jsonify(search_results), 200

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

    #set path url for error message object
    error_message['path'] = request.url

    #if no input parameters set then return error message
    if (name == ""):
        return jsonify(create_error_message("The country name input parameter cannot be empty.", request.url)), 400   

    #path can accept multiple country names, separated by a comma but several
    #countries contain a comma already in their name. If multiple country names input,  
    #separate by comma, cast to a sorted list, unless any of the names are in the below list
    name_comma_exceptions = ["BOLIVIA, PLURINATIONAL STATE OF",
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
    
    #check if input country is in above list, if not add to sorted comma separated list    
    if (name.upper() in name_comma_exceptions):
        names = [name]
    else:
        names = sorted(name.split(','))
    
    #list of country name exceptions that are converted into their more common name
    name_converted = {"UAE": "United Arab Emirates", "Brunei": "Brunei Darussalam", "Bolivia": "Bolivia, Plurinational State of", 
                      "Bosnia": "Bosnia and Herzegovina", "Bonaire": "Bonaire, Sint Eustatius and Saba", "DR Congo": 
                      "Congo, the Democratic Republic of the", "Ivory Coast": "Côte d'Ivoire", "Cape Verde": "Cabo Verde", 
                      "Cocos Islands": "Cocos (Keeling) Islands", "Falkland Islands": "Falkland Islands (Malvinas)", 
                      "Micronesia": "Micronesia, Federated States of", "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
                      "South Georgia": "South Georgia and the South Sandwich Islands", "Iran": "Iran, Islamic Republic of",
                      "North Korea": "Korea, Democratic People's Republic of", "South Korea": "Korea, Republic of", 
                      "Laos": "Lao People's Democratic Republic", "Moldova": "Moldova, Republic of", "Saint Martin": "Saint Martin (French part)",
                      "Macau": "Macao", "Pitcairn Islands": "Pitcairn", "South Georgia": "South Georgia and the South Sandwich Islands",
                      "Heard Island": "Heard Island and McDonald Islands", "Palestine": "Palestine, State of", 
                      "Saint Helena": "Saint Helena, Ascension and Tristan da Cunha", "St Helena": "Saint Helena, Ascension and Tristan da Cunha",              
                      "Saint Kitts": "Saint Kitts and Nevis", "St Kitts": "Saint Kitts and Nevis", "St Vincent": "Saint Vincent and the Grenadines", 
                      "St Lucia": "Saint Lucia", "Saint Vincent": "Saint Vincent and the Grenadines", "Russia": "Russian Federation", 
                      "Sao Tome and Principe":" São Tomé and Príncipe", "Sint Maarten": "Sint Maarten (Dutch part)", "Syria": "Syrian Arab Republic", 
                      "Svalbard": "Svalbard and Jan Mayen", "French Southern and Antarctic Lands": "French Southern Territories", "Turkey": "Türkiye", 
                      "Taiwan": "Taiwan, Province of China", "Tanzania": "Tanzania, United Republic of", "USA": "United States of America", 
                      "United States": "United States of America", "Vatican City": "Holy See", "Vatican": "Holy See", "Venezuela": 
                      "Venezuela, Bolivarian Republic of", "Virgin Islands, British": "British Virgin Islands"}
    
    #iterate over list of names, convert country names from name_converted dict, if applicable
    for name_ in range(0, len(names)):
        if (names[name_].title() in list(name_converted.keys())):
            names[name_] = name_converted[names[name_]]

    #remove all whitespace in any of the country names
    names = [name_.strip(' ') for name_ in names]

    #get list of available country names from iso3166 library, remove whitespace
    all_names_no_space = [name_.strip(' ') for name_ in list(iso3166.countries_by_name.keys())]
    
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

        #use iso3166 package to find corresponding alpha-2 code from its name
        alpha2_code.append(iso3166.countries_by_name[name_matches[0].upper()].alpha2)
    
    #get country data from ISO 3166-2 object, using alpha-2 code
    for code in alpha2_code:
        iso3166_2[code] = get_all_subdivisions()[code]

    #parse filter query string param
    filter_param = request.args.get('filter')

    #filter out attributes from filter query parameter, if applicable 
    if not (filter_param is None):
        iso3166_2 = filter_attributes(filter_param, iso3166_2)
        if (iso3166_2 == -1):
            return jsonify(create_error_message(f"Invalid attribute name input to filter query string parameter: {filter_param}. Refer to the list of supported attributes: {", ".join(all_attributes)}.", request.url)), 400             

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

    #set path url for error message object
    error_message['path'] = request.url

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

@app.route('/clear-cache')
@app.route('/api/clear-cache')
def clear_cache():
    """ Clear cache of Subdivisions class instance and all cached subdivision data. Mainly used for dev. """
    get_subdivision_instance.cache_clear()
    get_all_subdivisions.cache_clear()
    return 'Cache cleared'

@app.route('/version')
@app.route('/api/version')
def get_version():
    """ Get the current version of the iso3166-2 being used by the API. Mainly used for dev. """
    return get_subdivision_instance().__version__

# def handler(environ, start_response):
#     return app(environ, start_response)

if __name__ == '__main__':
    #run Flask app 
    app.run(debug=True)