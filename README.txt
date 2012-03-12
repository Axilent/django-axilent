Django-Axilent
==============

Django-Axilent is plugin for Django that allows easy integration into the Axilent platform.

Django-Axilent will accomplish the following goals:

1.  Storage of an Axilent profile in association with an auth_user model, or within a session.
2.  Triggers.
3.  Mapping between models and Axilent content - post updates on save signal.
4.  Programmatic Content Channel or Content Channel Group access.

Django-Axilent will rely on [Sharrock](https://github.com/Axilent/sharrock "Sharrock") for RPC services to Axilent.

Settings
--------

`AXILENT_ENDPOINT = 'https://www.axilent.net'` (Only used for development.  Will point to www.axilent.net by default.)

`AXILENT_API_KEY = 'YOUR API KEY'`

`AXILENT_API_VERSION = 'beta1'` The version of the API to address.  Current default is 'beta1'.

`AXILENT_FUNCTION_PATH = '/api'` Path to ordinary functions in the API.  Defaults to '/api'.

`AXILENT_RESOURCE_PATH = '/api/resource'` Path to resources in the API.  Defaults to '/api/resource'.

`AXILENT_PROJECT = 'YOUR PROJECT'` The name of the Axilent project to address.

The only setting that is absolutely necessary is `AXILENT_API_KEY`.  However in order to use content mappings you must also set `AXILENT_PROJECT`.

Finally, it's not a bad idea to explicitly set `AXILENT_API_VERSION`.  That way Django-Axilent will only address a new version of the API when you explicitly decide it should.  Otherwise it may wind up addressing a new version of the API if you update Django-Axilent.

The other settings are primarily used for Django-Axilent development.


