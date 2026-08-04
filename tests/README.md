# iso3166-2-api Tests <a name="TOP"></a>

All of the modules and functionalities of iso3166-2-api are thoroughly tested using the Python [unittest][unittest] framework.
## Module tests:

* `test_iso3166_2_api` - unit tests for iso3166-2 API, hosted on Vercel.

## Running Tests

To run all unittests, make sure you are in the main main directory and from a terminal/cmd-line run:
```python
python -m unittest discover tests -v
#-v produces a more verbose and useful output
```

The suite starts the Flask app itself on a free local port and runs against that, so no deployment
and no internet access is required. This means the tests exercise the code in the working tree
rather than whatever happens to be deployed, and they are not subject to the bot protection sitting
in front of the live deployment, which answers the `requests` library with a security checkpoint
page rather than JSON.

To run against a different instance instead, such as the live deployment, set `ISO3166_2_API_URL`:
```bash
ISO3166_2_API_URL="https://iso3166-2-api.vercel.app/api/" python -m unittest discover tests -v
```

[unittest]: https://docs.python.org/3/library/unittest.html