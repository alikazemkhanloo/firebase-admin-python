# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firebase Project Management module.

This module enables management of resources in Firebase projects, such as Android and iOS Apps.
"""

import time

import requests
import six

from firebase_admin import _http_client
from firebase_admin import _utils


_PROJECT_MANAGEMENT_ATTRIBUTE = '_project_management'


def _get_project_management_service(app):
    return _utils.get_app_service(app, _PROJECT_MANAGEMENT_ATTRIBUTE, _ProjectManagementService)


def android_app(app_id, app=None):
    """Obtains a reference to an Android App in the associated Firebase project.

    Args:
        app_id: The App ID that identifies this Android App.
        app: An App instance (optional).

    Returns:
        AndroidApp: An ``AndroidApp`` instance.
    """
    return AndroidApp(app_id=app_id, service=_get_project_management_service(app))


def ios_app(app_id, app=None):
    """Obtains a reference to an iOS App in the associated Firebase project.

    Args:
        app_id: The App ID that identifies this iOS App.
        app: An App instance (optional).

    Returns:
        IosApp: An ``IosApp`` instance.
    """
    return IosApp(app_id=app_id, service=_get_project_management_service(app))


def list_android_apps(app=None):
    """Lists all Android Apps in the associated Firebase project.

    Args:
        app: An App instance (optional).

    Returns:
        list: a list of ``AndroidApp`` instances referring to each Android App in the Firebase
            project.
    """
    return _get_project_management_service(app).list_android_apps()


def list_ios_apps(app=None):
    """Lists all iOS Apps in the associated Firebase project.

    Args:
        app: An App instance (optional).

    Returns:
        list: a list of ``IosApp`` instances referring to each iOS App in the Firebase project.
    """
    return _get_project_management_service(app).list_ios_apps()


def create_android_app(package_name, display_name=None, app=None):
    """Creates a new Android App in the associated Firebase project.

    Args:
        package_name: The package name of the Android App to be created.
        display_name: A nickname for this Android App (optional).
        app: An App instance (optional).

    Returns:
        AndroidApp: An ``AndroidApp`` instance that is a reference to the newly created App.
    """
    return _get_project_management_service(app).create_android_app(package_name, display_name)


def create_ios_app(bundle_id, display_name=None, app=None):
    """Creates a new iOS App in the associated Firebase project.

    Args:
        bundle_id: The bundle ID of the iOS App to be created.
        display_name: A nickname for this iOS App (optional).
        app: An App instance (optional).

    Returns:
        IosApp: An ``IosApp`` instance that is a reference to the newly created App.
    """
    return _get_project_management_service(app).create_ios_app(bundle_id, display_name)


def _check_is_string(obj, field_name):
    if isinstance(obj, six.string_types):
        return obj
    raise ValueError('{0} must be a string.'.format(field_name))


def _check_is_string_or_none(obj, field_name):
    if obj is None:
        return None
    return _check_is_string(obj, field_name)


def _check_is_nonempty_string(obj, field_name):
    if isinstance(obj, six.string_types) and obj:
        return obj
    raise ValueError('{0} must be a non-empty string.'.format(field_name))


class ApiCallError(Exception):
    """An error encountered while interacting with the Firebase Project Management Service."""

    def __init__(self, message, error):
        Exception.__init__(self, message)
        self.detail = error


class _PollingError(Exception):
    """An error encountered during the polling of an App's creation status."""

    def __init__(self, message):
        Exception.__init__(self, message)


class AndroidApp(object):
    """A reference to an Android App within a Firebase project.

    Please use the module-level function ``android_app(app_id)`` to obtain instances of this class
    instead of instantiating it directly.
    """

    def __init__(self, app_id, service):
        self._app_id = app_id
        self._service = service

    @property
    def app_id(self):
        return self._app_id

    def get_metadata(self):
        """Retrieves detailed information about this Android App.

        Note: this method makes an RPC.

        Returns:
            AndroidAppMetadata: An ``AndroidAppMetadata`` instance.

        Raises:
            ApiCallError: If an error occurs while communicating with the Firebase Project
                Management Service.
        """
        return self._service.get_android_app_metadata(self._app_id)

    def set_display_name(self, new_display_name):
        """Updates the Display Name attribute of this Android App to the one given.

        Note: this method makes an RPC.

        Args:
            new_display_name: The new Display Name for this Android App.

        Returns:
            NoneType: None.

        Raises:
            ApiCallError: If an error occurs while communicating with the Firebase Project
                Management Service.
        """
        return self._service.set_android_app_display_name(self._app_id, new_display_name)


class IosApp(object):
    """A reference to an iOS App within a Firebase project.

    Please use the module-level function ``ios_app(app_id)`` to obtain instances of this class
    instead of instantiating it directly.
    """

    def __init__(self, app_id, service):
        self._app_id = app_id
        self._service = service

    @property
    def app_id(self):
        return self._app_id

    def get_metadata(self):
        """Retrieves detailed information about this iOS App.

        Note: this method makes an RPC.

        Returns:
            IosAppMetadata: An ``IosAppMetadata`` instance.

        Raises:
            ApiCallError: If an error occurs while communicating with the Firebase Project
                Management Service.
        """
        return self._service.get_ios_app_metadata(self._app_id)

    def set_display_name(self, new_display_name):
        """Updates the Display Name attribute of this iOS App to the one given.

        Note: this method makes an RPC.

        Args:
            new_display_name: The new Display Name for this iOS App.

        Returns:
            NoneType: None.

        Raises:
            ApiCallError: If an error occurs while communicating with the Firebase Project
                Management Service.
        """
        return self._service.set_ios_app_display_name(self._app_id, new_display_name)


class _AppMetadata(object):
    """Detailed information about a Firebase Android or iOS App."""

    def __init__(self, name, app_id, display_name, project_id):
        self._name = _check_is_nonempty_string(name, 'name')
        self._app_id = _check_is_nonempty_string(app_id, 'app_id')
        self._display_name = _check_is_string(display_name, 'display_name')
        self._project_id = _check_is_nonempty_string(project_id, 'project_id')

    @property
    def name(self):
        """The fully qualified resource name of this Android or iOS App."""
        return self._name

    @property
    def app_id(self):
        """The globally unique, Firebase-assigned identifier of this Android or iOS App.

        This ID is unique even across Apps of different platforms.
        """
        return self._app_id

    @property
    def display_name(self):
        """The user-assigned display name of this Android or iOS App."""
        return self._display_name

    @property
    def project_id(self):
        """The permanent, globally unique, user-assigned ID of the parent Firebase project."""
        return self._project_id


class AndroidAppMetadata(_AppMetadata):
    """Android-specific information about an Android Firebase App."""

    def __init__(self, package_name, name, app_id, display_name, project_id):
        super(AndroidAppMetadata, self).__init__(name, app_id, display_name, project_id)
        self._package_name = _check_is_nonempty_string(package_name, 'package_name')

    @property
    def package_name(self):
        """The canonical package name of this Android App as it would appear in the Play Store."""
        return self._package_name


class IosAppMetadata(_AppMetadata):
    """iOS-specific information about an iOS Firebase App."""

    def __init__(self, bundle_id, name, app_id, display_name, project_id):
        super(IosAppMetadata, self).__init__(name, app_id, display_name, project_id)
        self._bundle_id = _check_is_nonempty_string(bundle_id, 'bundle_id')

    @property
    def bundle_id(self):
        """The canonical bundle ID of this iOS App as it would appear in the iOS AppStore."""
        return self._bundle_id


class _ProjectManagementService(object):
    """Provides methods for interacting with the Firebase Project Management Service."""

    BASE_URL = 'https://firebase.googleapis.com'
    MAXIMUM_LIST_APPS_PAGE_SIZE = 1
    MAXIMUM_POLLING_ATTEMPTS = 8
    POLL_BASE_WAIT_TIME_SECONDS = 0.5
    POLL_EXPONENTIAL_BACKOFF_FACTOR = 1.5
    ERROR_CODES = {
        401: 'Request not authorized.',
        403: 'Client does not have sufficient privileges.',
        404: 'Failed to find the resource.',
        409: 'The resource already exists.',
        429: 'Request throttled out by the backend server.',
        500: 'Internal server error.',
        503: 'Backend servers are over capacity. Try again later.'
    }

    ANDROID_APPS_RESOURCE_NAME = 'androidApps'
    ANDROID_APP_IDENTIFIER_NAME = 'packageName'
    ANDROID_APP_IDENTIFIER_LABEL = 'Package name'
    IOS_APPS_RESOURCE_NAME = 'iosApps'
    IOS_APP_IDENTIFIER_NAME = 'bundleId'
    IOS_APP_IDENTIFIER_LABEL = 'Bundle ID'

    def __init__(self, app):
        project_id = app.project_id
        if not project_id:
            raise ValueError(
                'Project ID is required to access the Firebase Project Management Service. Either '
                'set the projectId option, or use service account credentials. Alternatively, set '
                'the GOOGLE_CLOUD_PROJECT environment variable.')
        self._project_id = project_id
        self._client = _http_client.JsonHttpClient(
            credential=app.credential.get_credential(),
            base_url=_ProjectManagementService.BASE_URL)
        self._timeout = app.options.get('httpTimeout')

    def get_android_app_metadata(self, app_id):
        return self._get_app_metadata(
            platform_resource_name=_ProjectManagementService.ANDROID_APPS_RESOURCE_NAME,
            identifier_name=_ProjectManagementService.ANDROID_APP_IDENTIFIER_NAME,
            metadata_class=AndroidAppMetadata,
            app_id=app_id)

    def get_ios_app_metadata(self, app_id):
        return self._get_app_metadata(
            platform_resource_name=_ProjectManagementService.IOS_APPS_RESOURCE_NAME,
            identifier_name=_ProjectManagementService.IOS_APP_IDENTIFIER_NAME,
            metadata_class=IosAppMetadata,
            app_id=app_id)

    def _get_app_metadata(self, platform_resource_name, identifier_name, metadata_class, app_id):
        """Retrieves detailed information about an Android or iOS App."""
        _check_is_nonempty_string(app_id, 'app_id')
        path = '/v1beta1/projects/-/{0}/{1}'.format(platform_resource_name, app_id)
        response = self._make_request('get', path, app_id, 'App ID')
        return metadata_class(
            response[identifier_name],
            name=response['name'],
            app_id=response['appId'],
            display_name=self._none_to_empty(response.get('displayName')),
            project_id=response['projectId'])

    def set_android_app_display_name(self, app_id, new_display_name):
        self._set_display_name(
            app_id=app_id,
            new_display_name=new_display_name,
            platform_resource_name=_ProjectManagementService.ANDROID_APPS_RESOURCE_NAME)

    def set_ios_app_display_name(self, app_id, new_display_name):
        self._set_display_name(
            app_id=app_id,
            new_display_name=new_display_name,
            platform_resource_name=_ProjectManagementService.IOS_APPS_RESOURCE_NAME)

    def _set_display_name(self, app_id, new_display_name, platform_resource_name):
        """Sets the display name of an Android or iOS App."""
        path = '/v1beta1/projects/-/{0}/{1}?update_mask=display_name'.format(
            platform_resource_name, app_id)
        request_body = {'displayName': new_display_name}
        self._make_request('patch', path, app_id, 'App ID', json=request_body)

    def list_android_apps(self):
        return self._list_apps(
            platform_resource_name=_ProjectManagementService.ANDROID_APPS_RESOURCE_NAME,
            app_class=AndroidApp)

    def list_ios_apps(self):
        return self._list_apps(
            platform_resource_name=_ProjectManagementService.IOS_APPS_RESOURCE_NAME,
            app_class=IosApp)

    def _list_apps(self, platform_resource_name, app_class):
        """Lists all the Android or iOS Apps within the Firebase project."""
        path = '/v1beta1/projects/{0}/{1}?pageSize={2}'.format(
            self._project_id,
            platform_resource_name,
            _ProjectManagementService.MAXIMUM_LIST_APPS_PAGE_SIZE)
        response = self._make_request('get', path, self._project_id, 'Project ID')
        apps_list = []
        while True:
            apps = response.get('apps')
            if not apps:
                break
            apps_list.extend(app_class(app_id=app['appId'], service=self) for app in apps)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            # Retrieve the next page of Apps.
            path = '/v1beta1/projects/{0}/{1}?pageToken={2}&pageSize={3}'.format(
                self._project_id,
                platform_resource_name,
                next_page_token,
                _ProjectManagementService.MAXIMUM_LIST_APPS_PAGE_SIZE)
            response = self._make_request('get', path, self._project_id, 'Project ID')
        return apps_list

    def create_android_app(self, package_name, display_name=None):
        return self._create_app(
            platform_resource_name=_ProjectManagementService.ANDROID_APPS_RESOURCE_NAME,
            identifier_name=_ProjectManagementService.ANDROID_APP_IDENTIFIER_NAME,
            identifier_label=_ProjectManagementService.ANDROID_APP_IDENTIFIER_LABEL,
            identifier=package_name,
            display_name=display_name,
            app_class=AndroidApp)

    def create_ios_app(self, bundle_id, display_name=None):
        return self._create_app(
            platform_resource_name=_ProjectManagementService.IOS_APPS_RESOURCE_NAME,
            identifier_name=_ProjectManagementService.IOS_APP_IDENTIFIER_NAME,
            identifier_label=_ProjectManagementService.IOS_APP_IDENTIFIER_LABEL,
            identifier=bundle_id,
            display_name=display_name,
            app_class=IosApp)

    def _create_app(
            self,
            platform_resource_name,
            identifier_name,
            identifier_label,
            identifier,
            display_name,
            app_class):
        """Creates an Android or iOS App."""
        _check_is_string_or_none(display_name, 'display_name')
        path = '/v1beta1/projects/{0}/{1}'.format(self._project_id, platform_resource_name)
        request_body = {'displayName': display_name, identifier_name: identifier}
        response = self._make_request('post', path, identifier, identifier_label, json=request_body)
        operation_name = response['name']
        try:
            poll_response = self._poll_app_creation(operation_name)
            return app_class(app_id=poll_response['appId'], service=self)
        except _PollingError as error:
            raise ApiCallError(
                self._extract_message(operation_name, 'Operation name', error), error)

    def _poll_app_creation(self, operation_name):
        """Polls the Long-Running Operation repeatedly until it is done with exponential backoff."""
        for current_attempt in range(_ProjectManagementService.MAXIMUM_POLLING_ATTEMPTS):
            delay_factor = pow(
                _ProjectManagementService.POLL_EXPONENTIAL_BACKOFF_FACTOR, current_attempt)
            wait_time_seconds = delay_factor * _ProjectManagementService.POLL_BASE_WAIT_TIME_SECONDS
            time.sleep(wait_time_seconds)
            path = '/v1/{0}'.format(operation_name)
            poll_response = self._make_request('get', path, operation_name, 'Operation name')
            done = poll_response.get('done')
            if done:
                response = poll_response.get('response')
                if response:
                    return response
                else:
                    raise _PollingError('Operation terminated in an error.')
        raise _PollingError('Polling deadline exceeded.')

    def _make_request(self, method, url, resource_identifier, resource_identifier_label, json=None):
        try:
            return self._client.body(method=method, url=url, json=json, timeout=self._timeout)
        except requests.exceptions.RequestException as error:
            raise ApiCallError(
                self._extract_message(resource_identifier, resource_identifier_label, error), error)

    def _extract_message(self, identifier, identifier_label, error):
        if not isinstance(error, requests.exceptions.RequestException) or error.response is None:
            return str(error)
        status = error.response.status_code
        message = _ProjectManagementService.ERROR_CODES.get(status)
        if message:
            return '{0} "{1}": {2}'.format(identifier_label, identifier, message)
        return '{0} "{1}": Error {2}.'.format(identifier_label, identifier, status)

    def _none_to_empty(self, string):
        if not string:
            return ''
        return string
