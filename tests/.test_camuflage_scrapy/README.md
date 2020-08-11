## Tests ignored (prefix '.')

These tests are being ignored for two reasons:
1. test_tor_controller requires TOR installed and this installation don't work on Windows.
2. both tests are for configurations, not modules.

Mainly because of 2 we have to check if these tests are necessary. Maybe it makes more sense to have tutorial files.
