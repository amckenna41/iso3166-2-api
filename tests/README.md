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

[unittest]: https://docs.python.org/3/library/unittest.html