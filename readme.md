Python wrapper for the Tribune's Boundary Service app. This is both a library and a command-line app
that lets you geocode invididual addresses and/or get back the boundary they're a part of, if you
care about that.

You'll need to have an environment variable called BING_API_KEY that contains your Bing API key as a
string. This is because the geocoder uses Bing; if you just care about the boundary service and are
fine passing in a lat/long to the get_boundaries_for utility, you won't need that.

You'll also need to have requests installed; probably you'll want to run this in a virtualenv for
that reason.

To use the tool as a command-line utility, pass it an address and a boundary type:
    python boundaries.py "435 n michigan, chicago" police-beats

To see the supported boundary types:
    python boundaries.py --help
