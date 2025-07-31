<a name="TOP"></a>

# iso3166-2-api 🌎 
<!-- ![Vercel](https://vercelbadge.vercel.app/api/amckenna41/iso3166-2-api) -->
![Vercel](https://therealsujitk-vercel-badge.vercel.app/?app=iso3166-2-api)
[![pytest](https://github.com/amckenna41/iso3166-2-api/workflows/Building%20and%20Testing/badge.svg)](https://github.com/amckenna41/iso3166-2-api/actions?query=workflowBuilding%20and%20Testing)
[![iso3166_2](https://img.shields.io/pypi/v/iso3166-2)](https://pypi.org/project/iso3166-2)
[![Documentation Status](https://readthedocs.org/projects/iso3166-2/badge/?version=latest)](https://iso3166-2.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/github/license/amckenna41/iso3166-2)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/amckenna41/iso3166-2-api)](https://github.com/amckenna41/iso3166-2-api/issues)

<div alt="images" style="justify-content: center; display:flex; margin-left=50px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3d/Flag-map_of_the_world_%282017%29.png" alt="globe" height="200" width="500"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/e/e3/ISO_Logo_%28Red_square%29.svg" alt="iso" height="200" width="300"/>
</div>

> Frontend RESTful API for the [`iso3166-2`](https://github.com/amckenna41/iso3166-2) software and repo that returns a plethora of bespoke, valuable and useful attributes for the >5000 subdivisions/regions for all countries in the ISO 3166-2 standard. Built using the Python Flask framework and hosted on the Vercel platform.

The main API homepage and documentation is available via the URL: <b>[https://iso3166-2-api.vercel.app/api](https://iso3166-2-api.vercel.app/api)</b>

Quick Start 🏃
--------------
* Source code for main `iso3166-2` software package is available [here][iso3166_2_repo]
* A <b>demo</b> of the software and API is available [here][demo]
* A <b>Medium</b> article that dives deeper into `iso3166-2` is available [here][medium]

Table of Contents
-----------------
- [Introduction](#introduction)
- [Bespoke Features](#bespoke-features)
- [Usage](#usage)
- [Requirements](#requirements)
- [Issues](#issues)
- [Contact](#contact)
- [References](#references)

## Introduction
This repo contains the front and backend of the RESTful API created to accompany the [`iso3166-2`](https://github.com/amckenna41/iso3166-2) repository. The API returns a plethora of bespoke, useful and valuable subdivision data for all countries in the ISO 3166-2 standard. Built using the Python [Flask][flask] framework and hosted on the [Vercel][vercel] platform.

[`iso3166-2`](https://github.com/amckenna41/iso3166-2) is a lightweight custom-built Python package that can be used to access all of the world's ISO 3166-2 subdivision data. Here, subdivision can be used interchangeably with regions/states/provinces etc. Currently, the package and API support subdivision data from **250** officially assigned code elements within the ISO 3166-1, with **200** of these countries having recognized subdivisions (50 entires have 0 subdivisions), totalling **5,049** subdivisions across the whole dataset.

The full list of subdivision data attributes supported are:

* **Code** - ISO 3166-2 subdivision code
* **Name** - subdivision name
* **Local/other name** - subdivision name in local language or any alternative name/nickname it is commonly known by
* **Parent Code** - subdivision parent code
* **Type** - subdivision type, e.g. region, state, canton, parish etc
* **Latitude/Longitude** - subdivision coordinates
* **Flag** - subdivision flag from [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repo; this is another ISO 3166 related custom-built dataset of over **3500** regional/subdivision flags
* **History** - historical updates/changes to the subdivision code and naming conventions, as per the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repo.

## Bespoke Features

There are three main attributes supported by the software that make it stand out and add a significant amount of value and data per subdivision, in comparison to some the other iso3166-2 datasets, these are the **local/other name**, **flag** and **history** attributes.

### Local/Other names
One of the most <b>important</b> and <b>bespoke</b> attributes that the software supports, that many others do not, is the **local/other name** attribute. This attribute is built from a custom dataset of local language variants and alternative names/nicknames  for the <b>over 5000</b> subdivisions. In total there are <b>>3700</b> local/other names for the <b>>5000</b> subdivisions. Primarily, the attribute contains local language translations for the subdivisions, but many also include <b>nicknames</b> and **alternative variants** that the subdivision may be known by, either locally or globally. 

For each local/other name, the ISO 639 3 letter language code is used to identify the language of the name. Some translations do not have available ISO 639 codes, therefore the [Glottolog](https://glottolog.org/) or other databases (e.g [IETF](https://support.elucidat.com/hc/en-us/articles/6068623875217-IETF-language-tags)) language codes are used. Some example local/other name entries are: 
* **Sindh (Pakistan PK-SD)**: "سِنْدھ (urd), Sindh (eng), SD (eng), Mehran/Gateway (eng), Bab-ul-Islam/Gateway of Islam (eng)"
* **Central Singapore (Singapore SG-01)**: "Pusat Singapura (msa), 新加坡中部 (zho), மத்திய சிங்கப்பூர் (tam)"
* **Bobonaro (East Timor TL-BO)**: "Bobonaru (tet), Buburnaru (tet), Tall eucalypt (eng)"
* **Wyoming (USA US-WY)** - "Equality State (eng), Cowboy State (eng), Big Wyoming (eng)"

The full dataset of local/other names is available in the repo here [`local_other_names.csv`](https://github.com/amckenna41/iso3166-2/iso3166_2_resources/local_other_names.csv)


### Flags
The other equally important and bespoke/unique attribute that the software package supports is the ``flag`` attribute, which is a link to the subdivision's flag on the [`iso3166-flag-icons`](https://github.com/amckenna41/iso3166-flag-icons) repo. This is another **custom-built** repository, (alongside [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates)) that stores a rich and comprehensive dataset of over **3500** individual subdivision flags. 

The flags repo uses the `iso3166-2` software to get the full list of ISO 3166-2 subdivision codes which is kept up-to-date and accurate via the `iso3166-updates` software. 

   <div align="center">❤️ iso3166-2 🤝 iso3166-updates 🤝 iso3166-flag-icons ❤️</div>
   

### History
The `history` attribute has any applicable historical updates/changes to the individual subdivisions, if applicable. The data source for this is another custom-built software package previously mentioned [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates). This package keeps track of all the published changes that the ISO make to the ISO 3166 standard which include addition of new subdivisions, deletion of existing subdivisions or amendments to existing subdivisions. Thus [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) helps ensure that the data in the `iso3166-2` package is also kept up-to-date and accurate. If any updates are found for the subdivision a short description of the change, it's publication date as well as its source will be included.

   <div align="center">❤️ iso3166-2 🤝 iso3166-updates ❤️</div>

## Usage

Please refer to the [`API.md`](https://github.com/amckenna41/iso3166-2-api/API.md) file for API usage examples.


<!-- ## Staying up to date
An important thing to note about the ISO 3166-2 and its subdivision codes/names is that changes are made consistently to it, from a small subdivision name change to an addition/deletion of a whole subdivision. These changes can happen due to a variety of geopolitical and administrative reasons. Therefore, it's important that the [`iso3166-2`](https://github.com/amckenna41/iso3166-2) library and its dataset have the most up-to-date, accurate and reliable data. To achieve this, the custom-built [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repo was created.

The [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates) repo is another open-source software package and accompanying API that pulls the latest updates and changes for any and all countries in the ISO 3166 from a variety of data sources including the ISO website itself. A script is called every few months to check for any updates/changes to the subdivisions, which are communicated via the ISO's Online Browsing Platform [[4]](#references), and will then be manually incorporated into the [`iso3166-2`](https://github.com/amckenna41/iso3166-2) and dataset. Please visit the repository home page for more info about the purpose and process of the software and API - [`iso3166-updates`](https://github.com/amckenna41/iso3166-updates).

The list of ISO 3166 updates was last updated on <strong>June 2024</strong>. A log of the latest ISO 3166 updates can be seen in the [UPDATES.md][updates_md]. -->

## Requirements
* [python][python] >= 3.9
* [flask][flask] >= 2.3.2
* [requests][requests] >= 2.28.1
* [iso3166][iso3166] >= 2.1.1
* [iso3166-2][iso3166_2] >= 1.7.2
* [unidecode][unidecode] >= 1.3.8
* [thefuzz][thefuzz] >= 0.22.1

## Issues
Any issues, errors or enhancements can be raised via the [Issues](https://github.com/amckenna41/iso3166-2-api/issues) tab in the repository.

## Contact
If you have any questions or comments, please contact amckenna41@qub.ac.uk or raise an issue on the [Issues][Issues] tab. <br><br>

## Other ISO 3166 repositories
Below are some of my other custom-built repositories that relate to the ISO 3166 standard.

* [iso3166-2](https://github.com/amckenna41/iso3166-2):  a lightweight custom-built Python package that can be used to access all of the world's ISO 3166-2 subdivision data.  Currently, the package and API support subdivision data from **250** officially assigned code elements within the ISO 3166-1, with **200** of these countries having recognized subdivisions (50 entires have 0 subdivisions), totalling **5,049** subdivisions across the whole dataset.
* [iso3166-updates](https://github.com/amckenna41/iso3166-update): software and accompanying RESTful API that checks for any updates/changes to the ISO 3166-1 and ISO 3166-2 country codes and subdivision naming conventions, as per the ISO 3166 newsletter (https://www.iso.org/iso-3166-country-codes.html) and Online Browsing Platform (OBP) (https://www.iso.org/obp/ui).
* [iso3166-updates-api](https://github.com/amckenna41/iso3166-updates-api): frontend API for iso3166-updates.
* [iso3166-flag-icons](https://github.com/amckenna41/iso3166-flag-icons): a comprehensive library of over 3500 country and regional flags from the ISO 3166-1 and ISO 3166-2 standards.

## References
\[1\]: ISO3166-1: https://en.wikipedia.org/wiki/ISO_3166-1 <br>
\[2\]: ISO3166-2: https://en.wikipedia.org/wiki/ISO_3166-2 <br>
\[3\]: ISO Country Codes Collection: https://www.iso.org/publication/PUB500001 <br>
\[4\]: ISO Country Codes: https://www.iso.org/iso-3166-country-codes.html <br>
\[5\]: ISO3166-2 flag-icons repo: https://github.com/amckenna41/iso3166-flag-icons <br>

## Support
[<img src="https://img.shields.io/github/stars/amckenna41/iso3166-2-api?color=green&label=star%20it%20on%20GitHub" width="132" height="20" alt="Star it on GitHub">](https://github.com/amckenna41/iso3166-2-api)
<a href="https://www.buymeacoffee.com/amckenna41" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

[Back to top](#TOP)

[iso3166_2_repo]: https://github.com/amckenna41/iso3166-2
[demo]: https://colab.research.google.com/drive/1btfEx23bgWdkUPiwdwlDqKkmUp1S-_7U?usp=sharing
[flask]: https://flask.palletsprojects.com/en/2.3.x/
[python]: https://www.python.org/downloads/release/python-360/
[requests]: https://requests.readthedocs.io/
[iso3166]: https://github.com/deactivated/python-iso3166
[iso3166_2]: https://github.com/amckenna41/iso3166-2
[unidecode]: https://pypi.org/project/Unidecode/
[thefuzz]: https://github.com/seatgeek/thefuzz/tree/master
[google-auth]: https://cloud.google.com/python/docs/reference
[google-cloud-storage]: https://cloud.google.com/python/docs/reference
[google-api-python-client]: https://cloud.google.com/python/docs/reference
[Issues]: https://github.com/amckenna41/iso3166-2-api/issues
[vercel]: https://vercel.com/
[attributes]: https://github.com/amckenna41/iso3166-2-api/ATTRIBUTES.md 
[api_md]: https://github.com/amckenna41/iso3166-2-api/API.md 
[updates_md]: https://github.com/amckenna41/iso3166-2/blob/main/UPDATES.md
[medium]: https://ajmckenna69.medium.com/iso3166-2-71a13d9157f7