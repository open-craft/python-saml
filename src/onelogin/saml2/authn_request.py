# -*- coding: utf-8 -*-

""" OneLogin_Saml2_Authn_Request class

Copyright (c) 2014, OneLogin, Inc.
All rights reserved.

AuthNRequest class of OneLogin's Python Toolkit.

"""
from base64 import b64encode

from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class OneLogin_Saml2_Authn_Request(object):
    """

    This class handles an AuthNRequest. It builds an
    AuthNRequest object.

    """

    def __init__(self, settings, force_authn=False, is_passive=False):
        """
        Constructs the AuthnRequest object.

        :param settings: OSetting data
        :type return_to: OneLogin_Saml2_Settings

        :param force_authn: Optional argument. When true the AuthNReuqest will set the ForceAuthn='true'.
        :type force_authn: bool

        :param is_passive: Optional argument. When true the AuthNReuqest will set the Ispassive='true'.
        :type is_passive: bool
        """
        self.__settings = settings

        sp_data = self.__settings.get_sp_data()
        idp_data = self.__settings.get_idp_data()
        security = self.__settings.get_security_data()

        uid = OneLogin_Saml2_Utils.generate_unique_id()
        self.__id = uid
        issue_instant = OneLogin_Saml2_Utils.parse_time_to_SAML(OneLogin_Saml2_Utils.now())

        destination = idp_data['singleSignOnService']['url']

        name_id_policy_format = sp_data['NameIDFormat']
        if 'wantNameIdEncrypted' in security and security['wantNameIdEncrypted']:
            name_id_policy_format = OneLogin_Saml2_Constants.NAMEID_ENCRYPTED

        provider_name_str = ''
        organization_data = settings.get_organization()
        if isinstance(organization_data, dict) and organization_data:
            langs = organization_data.keys()
            if 'en-US' in langs:
                lang = 'en-US'
            else:
                lang = langs[0]
            if 'displayname' in organization_data[lang] and organization_data[lang]['displayname'] is not None:
                provider_name_str = 'ProviderName="%s"' % organization_data[lang]['displayname']

        force_authn_str = ''
        if force_authn is True:
            force_authn_str = 'ForceAuthn="true"'

        is_passive_str = ''
        if is_passive is True:
            is_passive_str = 'IsPassive="true"'

        requested_authn_context_str = ''
        if 'requestedAuthnContext' in security.keys() and security['requestedAuthnContext'] is not False:
            authn_comparison = 'exact'
            if 'requestedAuthnContextComparison' in security.keys():
                authn_comparison = security['requestedAuthnContextComparison']

            if security['requestedAuthnContext'] is True:
                requested_authn_context_str = """    <samlp:RequestedAuthnContext Comparison="%s">
        <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
    </samlp:RequestedAuthnContext>""" % authn_comparison
            else:
                requested_authn_context_str = '     <samlp:RequestedAuthnContext Comparison="%s">' % authn_comparison
                for authn_context in security['requestedAuthnContext']:
                    requested_authn_context_str += '<saml:AuthnContextClassRef>%s</saml:AuthnContextClassRef>' % authn_context
                requested_authn_context_str += '    </samlp:RequestedAuthnContext>'

        attr_consuming_service_str = ''
        if 'attributeConsumingService' in sp_data and sp_data['attributeConsumingService']:
            # TODO: Do we have to account for the case when we have multiple attributeconsumers?
            # like will the index be > 1?
            attr_consuming_service_str = 'AttributeConsumingServiceIndex="1"'

        request = """<samlp:AuthnRequest
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="%(id)s"
    Version="2.0"
    %(provider_name)s
    %(force_authn_str)s
    %(is_passive_str)s
    IssueInstant="%(issue_instant)s"
    Destination="%(destination)s"
    ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    AssertionConsumerServiceURL="%(assertion_url)s"
    %(attr_consuming_service_str)s>
    <saml:Issuer>%(entity_id)s</saml:Issuer>
    <samlp:NameIDPolicy
        Format="%(name_id_policy)s"
        AllowCreate="true" />
%(requested_authn_context_str)s
</samlp:AuthnRequest>""" % \
            {
                'id': uid,
                'provider_name': provider_name_str,
                'force_authn_str': force_authn_str,
                'is_passive_str': is_passive_str,
                'issue_instant': issue_instant,
                'destination': destination,
                'assertion_url': sp_data['assertionConsumerService']['url'],
                'entity_id': sp_data['entityId'],
                'name_id_policy': name_id_policy_format,
                'requested_authn_context_str': requested_authn_context_str,
                'attr_consuming_service_str': attr_consuming_service_str
            }

        self.__authn_request = request

    def get_request(self, deflate=True):
        """
        Returns unsigned AuthnRequest.
        :param deflate: It makes the deflate process optional
        :type: bool
        :return: AuthnRequest maybe deflated and base64 encoded
        :rtype: str object
        """
        if deflate:
            request = OneLogin_Saml2_Utils.deflate_and_base64_encode(self.__authn_request)
        else:
            request = b64encode(self.__authn_request)
        return request

    def get_id(self):
        """
        Returns the AuthNRequest ID.
        :return: AuthNRequest ID
        :rtype: string
        """
        return self.__id
