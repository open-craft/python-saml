# -*- coding: utf-8 -*-

# Copyright (c) 2014, OneLogin, Inc.
# All rights reserved.

import json
from os.path import dirname, join, exists, sep
import unittest

from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class OneLogin_Saml2_Settings_Test(unittest.TestCase):
    data_path = join(dirname(__file__), '..', '..', '..', 'data')
    settings_path = join(dirname(__file__), '..', '..', '..', 'settings')

    def loadSettingsJSON(self):
        filename = join(self.settings_path, 'settings1.json')
        if exists(filename):
            stream = open(filename, 'r')
            settings = json.load(stream)
            stream.close()
            return settings
        else:
            raise Exception('Settings json file does not exist')

    def file_contents(self, filename):
        f = open(filename, 'r')
        content = f.read()
        f.close()
        return content

    def testLoadSettingsFromDict(self):
        """
        Tests the OneLogin_Saml2_Settings Constructor.
        Case load setting from dict
        """
        settings_info = self.loadSettingsJSON()
        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertEqual(len(settings.get_errors()), 0)

        del settings_info['contactPerson']
        del settings_info['organization']
        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertEqual(len(settings.get_errors()), 0)

        del settings_info['security']
        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertEqual(len(settings.get_errors()), 0)

        del settings_info['sp']['NameIDFormats']
        del settings_info['idp']['NameIDPolicyFormat']
        del settings_info['idp']['NameIDPolicyAllowCreate']
        del settings_info['idp']['x509cert']
        settings_info['idp']['certFingerprint'] = 'afe71c28ef740bc87425be13a2263d37971daA1f9'
        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertEqual(len(settings.get_errors()), 0)

        settings_info['idp']['singleSignOnService']['url'] = 'invalid_url'
        try:
            settings_2 = OneLogin_Saml2_Settings(settings_info)
            self.assertNotEqual(len(settings_2.get_errors()), 0)
        except Exception as e:
            self.assertIn('Invalid dict settings: idp_sso_url_invalid', e.message)

        settings_info['idp']['singleSignOnService']['url'] = 'http://invalid_domain'
        try:
            settings_3 = OneLogin_Saml2_Settings(settings_info)
            self.assertNotEqual(len(settings_3.get_errors()), 0)
        except Exception as e:
            self.assertIn('Invalid dict settings: idp_sso_url_invalid', e.message)

        del settings_info['sp']
        del settings_info['idp']
        try:
            settings_4 = OneLogin_Saml2_Settings(settings_info)
            self.assertNotEqual(len(settings_4.get_errors()), 0)
        except Exception as e:
            self.assertIn('Invalid dict settings', e.message)
            self.assertIn('idp_not_found', e.message)
            self.assertIn('sp_not_found', e.message)

        settings_info = self.loadSettingsJSON()
        settings_info['security']['authnRequestsSigned'] = True
        settings_info['custom_base_path'] = dirname(__file__)
        try:
            settings_5 = OneLogin_Saml2_Settings(settings_info)
            self.assertNotEqual(len(settings_5.get_errors()), 0)
        except Exception as e:
            self.assertIn('Invalid dict settings: sp_cert_not_found_and_required', e.message)

        settings_info = self.loadSettingsJSON()
        settings_info['security']['nameIdEncrypted'] = True
        del settings_info['idp']['x509cert']
        try:
            settings_6 = OneLogin_Saml2_Settings(settings_info)
            self.assertNotEqual(len(settings_6.get_errors()), 0)
        except Exception as e:
            self.assertIn('Invalid dict settings: idp_cert_not_found_and_required', e.message)

    def testLoadSettingsFromInvalidData(self):
        """
        Tests the OneLogin_Saml2_Settings Constructor.
        Case load setting
        """
        invalid_settings = ('param1', 'param2')

        try:
            settings = OneLogin_Saml2_Settings(invalid_settings)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Unsupported settings object', e.message)

        settings = OneLogin_Saml2_Settings(custom_base_path=self.settings_path)
        self.assertEqual(len(settings.get_errors()), 0)

    def testLoadSettingsFromFile(self):
        """
        Tests the OneLogin_Saml2_Settings Constructor.
        Case load setting from file
        """
        custom_base_path = join(dirname(__file__), '..', '..', '..', 'settings')
        settings = OneLogin_Saml2_Settings(custom_base_path=custom_base_path)
        self.assertEqual(len(settings.get_errors()), 0)

        custom_base_path = dirname(__file__)
        try:
            OneLogin_Saml2_Settings(custom_base_path=custom_base_path)
        except Exception as e:
            self.assertIn('Settings file not found', e.message)

        custom_base_path = join(dirname(__file__), '..', '..', '..', 'data', 'customPath')
        settings_3 = OneLogin_Saml2_Settings(custom_base_path=custom_base_path)
        self.assertEqual(len(settings_3.get_errors()), 0)

    def testGetCertPath(self):
        """
        Tests getCertPath method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(custom_base_path=self.settings_path)
        self.assertEqual(self.settings_path + sep + 'certs' + sep, settings.get_cert_path())

    def testGetLibPath(self):
        """
        Tests getLibPath method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(custom_base_path=self.settings_path)
        base = settings.get_base_path()
        self.assertEqual(join(base, 'lib') + sep, settings.get_lib_path())

    def testGetExtLibPath(self):
        """
        Tests getExtLibPath method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(custom_base_path=self.settings_path)
        base = settings.get_base_path()
        self.assertEqual(join(base, 'extlib') + sep, settings.get_ext_lib_path())

    def testGetSchemasPath(self):
        """
        Tests getSchemasPath method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(custom_base_path=self.settings_path)
        base = settings.get_base_path()
        self.assertEqual(join(base, 'lib', 'schemas') + sep, settings.get_schemas_path())

    def testGetSPCert(self):
        """
        Tests the get_sp_cert method of the OneLogin_Saml2_Settings
        """
        settings_data = self.loadSettingsJSON()
        cert = "-----BEGIN CERTIFICATE-----\nMIICgTCCAeoCCQCbOlrWDdX7FTANBgkqhkiG9w0BAQUFADCBhDELMAkGA1UEBhMC\nTk8xGDAWBgNVBAgTD0FuZHJlYXMgU29sYmVyZzEMMAoGA1UEBxMDRm9vMRAwDgYD\nVQQKEwdVTklORVRUMRgwFgYDVQQDEw9mZWlkZS5lcmxhbmcubm8xITAfBgkqhkiG\n9w0BCQEWEmFuZHJlYXNAdW5pbmV0dC5ubzAeFw0wNzA2MTUxMjAxMzVaFw0wNzA4\nMTQxMjAxMzVaMIGEMQswCQYDVQQGEwJOTzEYMBYGA1UECBMPQW5kcmVhcyBTb2xi\nZXJnMQwwCgYDVQQHEwNGb28xEDAOBgNVBAoTB1VOSU5FVFQxGDAWBgNVBAMTD2Zl\naWRlLmVybGFuZy5ubzEhMB8GCSqGSIb3DQEJARYSYW5kcmVhc0B1bmluZXR0Lm5v\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDivbhR7P516x/S3BqKxupQe0LO\nNoliupiBOesCO3SHbDrl3+q9IbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHIS\nKOtPlAeTZSnb8QAu7aRjZq3+PbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d\n1EDwXJW1rRXuUt4C8QIDAQABMA0GCSqGSIb3DQEBBQUAA4GBACDVfp86HObqY+e8\nBUoWQ9+VMQx1ASDohBjwOsg2WykUqRXF+dLfcUH9dWR63CtZIKFDbStNomPnQz7n\nbK+onygwBspVEbnHuUihZq3ZUdmumQqCw4Uvs/1Uvq3orOo/WJVhTyvLgFVK2Qar\nQ4/67OZfHd7R+POBXhophSMv1ZOo\n-----END CERTIFICATE-----\n"
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert, settings.get_sp_cert())

        cert_2 = "-----BEGIN CERTIFICATE-----\nMIICbDCCAdWgAwIBAgIBADANBgkqhkiG9w0BAQ0FADBTMQswCQYDVQQGEwJ1czET\nMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UECgwMT25lbG9naW4gSW5jMRgwFgYD\nVQQDDA9pZHAuZXhhbXBsZS5jb20wHhcNMTQwOTIzMTIyNDA4WhcNNDIwMjA4MTIy\nNDA4WjBTMQswCQYDVQQGEwJ1czETMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UE\nCgwMT25lbG9naW4gSW5jMRgwFgYDVQQDDA9pZHAuZXhhbXBsZS5jb20wgZ8wDQYJ\nKoZIhvcNAQEBBQADgY0AMIGJAoGBAOWA+YHU7cvPOrBOfxCscsYTJB+kH3MaA9BF\nrSHFS+KcR6cw7oPSktIJxUgvDpQbtfNcOkE/tuOPBDoech7AXfvH6d7Bw7xtW8PP\nJ2mB5Hn/HGW2roYhxmfh3tR5SdwN6i4ERVF8eLkvwCHsNQyK2Ref0DAJvpBNZMHC\npS24916/AgMBAAGjUDBOMB0GA1UdDgQWBBQ77/qVeiigfhYDITplCNtJKZTM8DAf\nBgNVHSMEGDAWgBQ77/qVeiigfhYDITplCNtJKZTM8DAMBgNVHRMEBTADAQH/MA0G\nCSqGSIb3DQEBDQUAA4GBAJO2j/1uO80E5C2PM6Fk9mzerrbkxl7AZ/mvlbOn+sNZ\nE+VZ1AntYuG8ekbJpJtG1YfRfc7EA9mEtqvv4dhv7zBy4nK49OR+KpIBjItWB5kY\nvrqMLKBa32sMbgqqUqeF1ENXKjpvLSuPdfGJZA3dNa/+Dyb8GGqWe707zLyc5F8m\n-----END CERTIFICATE-----\n"
        settings_data['sp']['x509cert'] = cert_2
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert_2, settings.get_sp_cert())

        del settings_data['sp']['x509cert']
        del settings_data['custom_base_path']
        custom_base_path = dirname(__file__)

        settings_3 = OneLogin_Saml2_Settings(settings_data, custom_base_path=custom_base_path)
        self.assertIsNone(settings_3.get_sp_cert())

    def testGetSPKey(self):
        """
        Tests the get_sp_key method of the OneLogin_Saml2_Settings
        """
        settings_data = self.loadSettingsJSON()
        key = "-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQDivbhR7P516x/S3BqKxupQe0LONoliupiBOesCO3SHbDrl3+q9\nIbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHISKOtPlAeTZSnb8QAu7aRjZq3+\nPbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d1EDwXJW1rRXuUt4C8QIDAQAB\nAoGAD4/Z4LWVWV6D1qMIp1Gzr0ZmdWTE1SPdZ7Ej8glGnCzPdguCPuzbhGXmIg0V\nJ5D+02wsqws1zd48JSMXXM8zkYZVwQYIPUsNn5FetQpwxDIMPmhHg+QNBgwOnk8J\nK2sIjjLPL7qY7Itv7LT7Gvm5qSOkZ33RCgXcgz+okEIQMYkCQQDzbTOyDL0c5WQV\n6A2k06T/azdhUdGXF9C0+WkWSfNaovmTgRXh1G+jMlr82Snz4p4/STt7P/XtyWzF\n3pkVgZr3AkEA7nPjXwHlttNEMo6AtxHd47nizK2NUN803ElIUT8P9KSCoERmSXq6\n6PDekGNic4ldpsSvOeYCk8MAYoDBy9kvVwJBAMLgX4xg6lzhv7hR5+pWjTb1rIY6\nrCHbrPfU264+UZXz9v2BT/VUznLF81WMvStD9xAPHpFS6R0OLghSZhdzhI0CQQDL\n8Duvfxzrn4b9QlmduV8wLERoT6rEVxKLsPVz316TGrxJvBZLk/cV0SRZE1cZf4uk\nXSWMfEcJ/0Zt+LdG1CqjAkEAqwLSglJ9Dy3HpgMz4vAAyZWzAxvyA1zW0no9GOLc\nPQnYaNUN/Fy2SYtETXTb0CQ9X1rt8ffkFP7ya+5TC83aMg==\n-----END RSA PRIVATE KEY-----\n"
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(key, settings.get_sp_key())

        key_2 = "-----BEGIN PRIVATE KEY-----\nMIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAOWA+YHU7cvPOrBO\nfxCscsYTJB+kH3MaA9BFrSHFS+KcR6cw7oPSktIJxUgvDpQbtfNcOkE/tuOPBDoe\nch7AXfvH6d7Bw7xtW8PPJ2mB5Hn/HGW2roYhxmfh3tR5SdwN6i4ERVF8eLkvwCHs\nNQyK2Ref0DAJvpBNZMHCpS24916/AgMBAAECgYEA0wDXZPS9hKqMTNh+nnfONioX\nBjhA6fQ7GVtWKDxa3ofMoPyt7ejGL/Hnvcv13Vn02UAsFx1bKrCstDqVtYwrWrnm\nywXyH+o9paJnTmd+cRIjWU8mRvCrxzH5I/Bcvbp1qZoASuqZEaGwNjM6JpW2o3QT\nmHGMALcLUPfEvhApssECQQDy2e65E86HcFhi/Ta8TQ0odDCNbiWA0bI1Iu8B7z+N\nAy1D1+WnCd7w2u9U6CF/k2nFHCsvxEoeANM0z7h5T/XvAkEA8e4JqKmDrfdiakQT\n7nf9svU2jXZtxSbPiIRMafNikDvzZ1vJCZkvdmaWYL70GlDZIwc9ad67rHZ/n/fq\nX1d0MQJAbRpRsJ5gY+KqItbFt3UaWzlP8sowWR5cZJjsLb9RmsV5mYguKYw6t5R0\nf33GRu1wUFimYlBaR/5w5MIJi57LywJATO1a5uWX+G5MPewNxmsjIY91XEAHIYR4\nwzkGLz5z3dciS4BVCZdLD0QJlxPA/MkuckPwFET9uhYn+M7VGKHvUQJBANSDwsY+\nBdCGpi/WRV37HUfwLl07damaFbW3h08PQx8G8SuF7DpN+FPBcI6VhzrIWNRBxWpr\nkgeGioKNfFWzSaM=\n-----END PRIVATE KEY-----\n"
        settings_data['sp']['privateKey'] = key_2
        settings_2 = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(key_2, settings_2.get_sp_key())

        del settings_data['sp']['privateKey']
        del settings_data['custom_base_path']
        custom_base_path = dirname(__file__)

        settings_3 = OneLogin_Saml2_Settings(settings_data, custom_base_path=custom_base_path)
        self.assertIsNone(settings_3.get_sp_key())

    def testFormatIdPCert(self):
        """
        Tests the format_idp_cert method of the OneLogin_Saml2_Settings
        """
        settings_data = self.loadSettingsJSON()
        cert = "-----BEGIN CERTIFICATE-----\nMIICgTCCAeoCCQCbOlrWDdX7FTANBgkqhkiG9w0BAQUFADCBhDELMAkGA1UEBhMC\nTk8xGDAWBgNVBAgTD0FuZHJlYXMgU29sYmVyZzEMMAoGA1UEBxMDRm9vMRAwDgYD\nVQQKEwdVTklORVRUMRgwFgYDVQQDEw9mZWlkZS5lcmxhbmcubm8xITAfBgkqhkiG\n9w0BCQEWEmFuZHJlYXNAdW5pbmV0dC5ubzAeFw0wNzA2MTUxMjAxMzVaFw0wNzA4\nMTQxMjAxMzVaMIGEMQswCQYDVQQGEwJOTzEYMBYGA1UECBMPQW5kcmVhcyBTb2xi\nZXJnMQwwCgYDVQQHEwNGb28xEDAOBgNVBAoTB1VOSU5FVFQxGDAWBgNVBAMTD2Zl\naWRlLmVybGFuZy5ubzEhMB8GCSqGSIb3DQEJARYSYW5kcmVhc0B1bmluZXR0Lm5v\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDivbhR7P516x/S3BqKxupQe0LO\nNoliupiBOesCO3SHbDrl3+q9IbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHIS\nKOtPlAeTZSnb8QAu7aRjZq3+PbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d\n1EDwXJW1rRXuUt4C8QIDAQABMA0GCSqGSIb3DQEBBQUAA4GBACDVfp86HObqY+e8\nBUoWQ9+VMQx1ASDohBjwOsg2WykUqRXF+dLfcUH9dWR63CtZIKFDbStNomPnQz7n\nbK+onygwBspVEbnHuUihZq3ZUdmumQqCw4Uvs/1Uvq3orOo/WJVhTyvLgFVK2Qar\nQ4/67OZfHd7R+POBXhophSMv1ZOo\n-----END CERTIFICATE-----\n"
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert, settings.get_idp_cert())

        cert_2 = "-----BEGIN CERTIFICATE-----\nMIICbDCCAdWgAwIBAgIBADANBgkqhkiG9w0BAQ0FADBTMQswCQYDVQQGEwJ1czET\nMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UECgwMT25lbG9naW4gSW5jMRgwFgYD\nVQQDDA9pZHAuZXhhbXBsZS5jb20wHhcNMTQwOTIzMTIyNDA4WhcNNDIwMjA4MTIy\nNDA4WjBTMQswCQYDVQQGEwJ1czETMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UE\nCgwMT25lbG9naW4gSW5jMRgwFgYDVQQDDA9pZHAuZXhhbXBsZS5jb20wgZ8wDQYJ\nKoZIhvcNAQEBBQADgY0AMIGJAoGBAOWA+YHU7cvPOrBOfxCscsYTJB+kH3MaA9BF\nrSHFS+KcR6cw7oPSktIJxUgvDpQbtfNcOkE/tuOPBDoech7AXfvH6d7Bw7xtW8PP\nJ2mB5Hn/HGW2roYhxmfh3tR5SdwN6i4ERVF8eLkvwCHsNQyK2Ref0DAJvpBNZMHC\npS24916/AgMBAAGjUDBOMB0GA1UdDgQWBBQ77/qVeiigfhYDITplCNtJKZTM8DAf\nBgNVHSMEGDAWgBQ77/qVeiigfhYDITplCNtJKZTM8DAMBgNVHRMEBTADAQH/MA0G\nCSqGSIb3DQEBDQUAA4GBAJO2j/1uO80E5C2PM6Fk9mzerrbkxl7AZ/mvlbOn+sNZ\nE+VZ1AntYuG8ekbJpJtG1YfRfc7EA9mEtqvv4dhv7zBy4nK49OR+KpIBjItWB5kY\nvrqMLKBa32sMbgqqUqeF1ENXKjpvLSuPdfGJZA3dNa/+Dyb8GGqWe707zLyc5F8m\n-----END CERTIFICATE-----\n"
        settings_data['idp']['x509cert'] = cert_2
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert_2, settings.get_idp_cert())

    def testFormatSPCert(self):
        """
        Tests the format_sp_cert method of the OneLogin_Saml2_Settings
        """
        settings_data = self.loadSettingsJSON()

        cert = "-----BEGIN CERTIFICATE-----\nMIICgTCCAeoCCQCbOlrWDdX7FTANBgkqhkiG9w0BAQUFADCBhDELMAkGA1UEBhMC\nTk8xGDAWBgNVBAgTD0FuZHJlYXMgU29sYmVyZzEMMAoGA1UEBxMDRm9vMRAwDgYD\nVQQKEwdVTklORVRUMRgwFgYDVQQDEw9mZWlkZS5lcmxhbmcubm8xITAfBgkqhkiG\n9w0BCQEWEmFuZHJlYXNAdW5pbmV0dC5ubzAeFw0wNzA2MTUxMjAxMzVaFw0wNzA4\nMTQxMjAxMzVaMIGEMQswCQYDVQQGEwJOTzEYMBYGA1UECBMPQW5kcmVhcyBTb2xi\nZXJnMQwwCgYDVQQHEwNGb28xEDAOBgNVBAoTB1VOSU5FVFQxGDAWBgNVBAMTD2Zl\naWRlLmVybGFuZy5ubzEhMB8GCSqGSIb3DQEJARYSYW5kcmVhc0B1bmluZXR0Lm5v\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDivbhR7P516x/S3BqKxupQe0LO\nNoliupiBOesCO3SHbDrl3+q9IbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHIS\nKOtPlAeTZSnb8QAu7aRjZq3+PbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d\n1EDwXJW1rRXuUt4C8QIDAQABMA0GCSqGSIb3DQEBBQUAA4GBACDVfp86HObqY+e8\nBUoWQ9+VMQx1ASDohBjwOsg2WykUqRXF+dLfcUH9dWR63CtZIKFDbStNomPnQz7n\nbK+onygwBspVEbnHuUihZq3ZUdmumQqCw4Uvs/1Uvq3orOo/WJVhTyvLgFVK2Qar\nQ4/67OZfHd7R+POBXhophSMv1ZOo\n-----END CERTIFICATE-----\n"
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert, settings.get_sp_cert())

        settings_data['sp']['x509cert'] = cert
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert, settings.get_sp_cert())

        cert_2 = "-----BEGIN CERTIFICATE-----\nMIICbDCCAdWgAwIBAgIBADANBgkqhkiG9w0BAQ0FADBTMQswCQYDVQQGEwJ1czET\nMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UECgwMT25lbG9naW4gSW5jMRgwFgYD\nVQQDDA9pZHAuZXhhbXBsZS5jb20wHhcNMTQwOTIzMTIyNDA4WhcNNDIwMjA4MTIy\nNDA4WjBTMQswCQYDVQQGEwJ1czETMBEGA1UECAwKQ2FsaWZvcm5pYTEVMBMGA1UE\nCgwMT25lbG9naW4gSW5jMRgwFgYDVQQDDA9pZHAuZXhhbXBsZS5jb20wgZ8wDQYJ\nKoZIhvcNAQEBBQADgY0AMIGJAoGBAOWA+YHU7cvPOrBOfxCscsYTJB+kH3MaA9BF\nrSHFS+KcR6cw7oPSktIJxUgvDpQbtfNcOkE/tuOPBDoech7AXfvH6d7Bw7xtW8PP\nJ2mB5Hn/HGW2roYhxmfh3tR5SdwN6i4ERVF8eLkvwCHsNQyK2Ref0DAJvpBNZMHC\npS24916/AgMBAAGjUDBOMB0GA1UdDgQWBBQ77/qVeiigfhYDITplCNtJKZTM8DAf\nBgNVHSMEGDAWgBQ77/qVeiigfhYDITplCNtJKZTM8DAMBgNVHRMEBTADAQH/MA0G\nCSqGSIb3DQEBDQUAA4GBAJO2j/1uO80E5C2PM6Fk9mzerrbkxl7AZ/mvlbOn+sNZ\nE+VZ1AntYuG8ekbJpJtG1YfRfc7EA9mEtqvv4dhv7zBy4nK49OR+KpIBjItWB5kY\nvrqMLKBa32sMbgqqUqeF1ENXKjpvLSuPdfGJZA3dNa/+Dyb8GGqWe707zLyc5F8m\n-----END CERTIFICATE-----\n"
        settings_data['sp']['x509cert'] = cert_2
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(cert_2, settings.get_sp_cert())

    def testFormatSPKey(self):
        """
        Tests the format_sp_key method of the OneLogin_Saml2_Settings
        """
        settings_data = self.loadSettingsJSON()
        key = "-----BEGIN RSA PRIVATE KEY-----\nMIICXgIBAAKBgQDivbhR7P516x/S3BqKxupQe0LONoliupiBOesCO3SHbDrl3+q9\nIbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHISKOtPlAeTZSnb8QAu7aRjZq3+\nPbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d1EDwXJW1rRXuUt4C8QIDAQAB\nAoGAD4/Z4LWVWV6D1qMIp1Gzr0ZmdWTE1SPdZ7Ej8glGnCzPdguCPuzbhGXmIg0V\nJ5D+02wsqws1zd48JSMXXM8zkYZVwQYIPUsNn5FetQpwxDIMPmhHg+QNBgwOnk8J\nK2sIjjLPL7qY7Itv7LT7Gvm5qSOkZ33RCgXcgz+okEIQMYkCQQDzbTOyDL0c5WQV\n6A2k06T/azdhUdGXF9C0+WkWSfNaovmTgRXh1G+jMlr82Snz4p4/STt7P/XtyWzF\n3pkVgZr3AkEA7nPjXwHlttNEMo6AtxHd47nizK2NUN803ElIUT8P9KSCoERmSXq6\n6PDekGNic4ldpsSvOeYCk8MAYoDBy9kvVwJBAMLgX4xg6lzhv7hR5+pWjTb1rIY6\nrCHbrPfU264+UZXz9v2BT/VUznLF81WMvStD9xAPHpFS6R0OLghSZhdzhI0CQQDL\n8Duvfxzrn4b9QlmduV8wLERoT6rEVxKLsPVz316TGrxJvBZLk/cV0SRZE1cZf4uk\nXSWMfEcJ/0Zt+LdG1CqjAkEAqwLSglJ9Dy3HpgMz4vAAyZWzAxvyA1zW0no9GOLc\nPQnYaNUN/Fy2SYtETXTb0CQ9X1rt8ffkFP7ya+5TC83aMg==\n-----END RSA PRIVATE KEY-----\n"
        settings_data['sp']['privateKey'] = key
        settings = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(key, settings.get_sp_key())

        key_2 = "-----BEGIN PRIVATE KEY-----\nMIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAOWA+YHU7cvPOrBO\nfxCscsYTJB+kH3MaA9BFrSHFS+KcR6cw7oPSktIJxUgvDpQbtfNcOkE/tuOPBDoe\nch7AXfvH6d7Bw7xtW8PPJ2mB5Hn/HGW2roYhxmfh3tR5SdwN6i4ERVF8eLkvwCHs\nNQyK2Ref0DAJvpBNZMHCpS24916/AgMBAAECgYEA0wDXZPS9hKqMTNh+nnfONioX\nBjhA6fQ7GVtWKDxa3ofMoPyt7ejGL/Hnvcv13Vn02UAsFx1bKrCstDqVtYwrWrnm\nywXyH+o9paJnTmd+cRIjWU8mRvCrxzH5I/Bcvbp1qZoASuqZEaGwNjM6JpW2o3QT\nmHGMALcLUPfEvhApssECQQDy2e65E86HcFhi/Ta8TQ0odDCNbiWA0bI1Iu8B7z+N\nAy1D1+WnCd7w2u9U6CF/k2nFHCsvxEoeANM0z7h5T/XvAkEA8e4JqKmDrfdiakQT\n7nf9svU2jXZtxSbPiIRMafNikDvzZ1vJCZkvdmaWYL70GlDZIwc9ad67rHZ/n/fq\nX1d0MQJAbRpRsJ5gY+KqItbFt3UaWzlP8sowWR5cZJjsLb9RmsV5mYguKYw6t5R0\nf33GRu1wUFimYlBaR/5w5MIJi57LywJATO1a5uWX+G5MPewNxmsjIY91XEAHIYR4\nwzkGLz5z3dciS4BVCZdLD0QJlxPA/MkuckPwFET9uhYn+M7VGKHvUQJBANSDwsY+\nBdCGpi/WRV37HUfwLl07damaFbW3h08PQx8G8SuF7DpN+FPBcI6VhzrIWNRBxWpr\nkgeGioKNfFWzSaM=\n-----END PRIVATE KEY-----\n"
        settings_data['sp']['privateKey'] = key_2
        settings_2 = OneLogin_Saml2_Settings(settings_data)
        self.assertEqual(key_2, settings_2.get_sp_key())

    def testCheckSPCerts(self):
        """
        Tests the checkSPCerts method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        self.assertTrue(settings.check_sp_certs())

    def testCheckSettings(self):
        """
        Tests the checkSettings method of the OneLogin_Saml2_Settings
        The checkSettings method is private and is used at the constructor
        """
        settings_info = {}
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Invalid dict settings: invalid_syntax', e.message)

        settings_info['strict'] = True
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('idp_not_found', e.message)
            self.assertIn('sp_not_found', e.message)

        settings_info['idp'] = {}
        settings_info['idp']['x509cert'] = ''
        settings_info['sp'] = {}
        settings_info['sp']['entityID'] = 'SPentityId'
        settings_info['security'] = {}
        settings_info['security']['signMetadata'] = False
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('idp_entityId_not_found', e.message)
            self.assertIn('idp_sso_not_found', e.message)
            self.assertIn('sp_entityId_not_found', e.message)
            self.assertIn('sp_acs_not_found', e.message)

        settings_info['idp']['entityID'] = 'entityId'
        settings_info['idp']['singleSignOnService'] = {}
        settings_info['idp']['singleSignOnService']['url'] = 'invalid_value'
        settings_info['idp']['singleLogoutService'] = {}
        settings_info['idp']['singleLogoutService']['url'] = 'invalid_value'
        settings_info['sp']['assertionConsumerService'] = {}
        settings_info['sp']['assertionConsumerService']['url'] = 'invalid_value'
        settings_info['sp']['singleLogoutService'] = {}
        settings_info['sp']['singleLogoutService']['url'] = 'invalid_value'
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('idp_sso_url_invalid', e.message)
            self.assertIn('idp_slo_url_invalid', e.message)
            self.assertIn('sp_acs_url_invalid', e.message)
            self.assertIn('sp_sls_url_invalid', e.message)

        settings_info['security']['wantAssertionsSigned'] = True
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('idp_cert_or_fingerprint_not_found_and_required', e.message)

        settings_info = self.loadSettingsJSON()
        settings_info['security']['signMetadata'] = {}
        settings_info['security']['signMetadata']['keyFileName'] = 'metadata.key'
        settings_info['organization'] = {
            'en-US': {
                'name': 'miss_information'
            }
        }
        settings_info['contactPerson'] = {
            'support': {
                'givenName': 'support_name'
            },
            'auxiliar': {
                'givenName': 'auxiliar_name',
                'emailAddress': 'auxiliar@example.com'
            }
        }
        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('sp_signMetadata_invalid', e.message)
            self.assertIn('organization_not_enought_data', e.message)
            self.assertIn('contact_type_invalid', e.message)

    def testGetSPMetadata(self):
        """
        Tests the getSPMetadata method of the OneLogin_Saml2_Settings
        Case unsigned metadata
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        metadata = settings.get_sp_metadata()

        self.assertNotEqual(len(metadata), 0)
        self.assertIn('<md:SPSSODescriptor', metadata)
        self.assertIn('entityID="http://stuff.com/endpoints/metadata.php"', metadata)
        self.assertIn('AuthnRequestsSigned="false"', metadata)
        self.assertIn('WantAssertionsSigned="false"', metadata)
        self.assertIn('<md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="http://stuff.com/endpoints/endpoints/acs.php" index="1"/>', metadata)
        self.assertIn('<md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="http://stuff.com/endpoints/endpoints/sls.php"/>', metadata)
        self.assertIn('<md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified</md:NameIDFormat>', metadata)

    def testGetSPMetadataSigned(self):
        """
        Tests the getSPMetadata method of the OneLogin_Saml2_Settings
        Case signed metadata
        """
        settings_info = self.loadSettingsJSON()
        if 'security' not in settings_info:
            settings_info['security'] = {}
        settings_info['security']['signMetadata'] = True
        settings = OneLogin_Saml2_Settings(settings_info)

        metadata = settings.get_sp_metadata()
        self.assertIn('<md:SPSSODescriptor', metadata)
        self.assertIn('entityID="http://stuff.com/endpoints/metadata.php"', metadata)
        self.assertIn('AuthnRequestsSigned="false"', metadata)
        self.assertIn('WantAssertionsSigned="false"', metadata)
        self.assertIn('<md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Location="http://stuff.com/endpoints/endpoints/acs.php" index="1"/>', metadata)
        self.assertIn('<md:SingleLogoutService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="http://stuff.com/endpoints/endpoints/sls.php"/>', metadata)
        self.assertIn('<md:NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified</md:NameIDFormat>', metadata)
        self.assertIn('<ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>', metadata)
        self.assertIn('<ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>', metadata)
        self.assertIn('<ds:Reference', metadata)
        self.assertIn('<ds:KeyInfo><ds:X509Data><ds:X509Certificate>', metadata)

    def testGetSPMetadataSignedNoMetadataCert(self):
        """
        Tests the getSPMetadata method of the OneLogin_Saml2_Settings
        Case signed metadata with specific certs
        """
        settings_info = self.loadSettingsJSON()
        if 'security' not in settings_info:
            settings_info['security'] = {}
        settings_info['security']['signMetadata'] = {}

        try:
            OneLogin_Saml2_Settings(settings_info)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('sp_signMetadata_invalid', e.message)

        settings_info['security']['signMetadata'] = {
            'keyFileName': 'noexist.key',
            'certFileName': 'sp.crt'
        }
        settings = OneLogin_Saml2_Settings(settings_info)
        try:
            settings.get_sp_metadata()
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Private key file not found', e.message)

        settings_info['security']['signMetadata'] = {
            'keyFileName': 'sp.key',
            'certFileName': 'noexist.crt'
        }
        settings = OneLogin_Saml2_Settings(settings_info)
        try:
            settings.get_sp_metadata()
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Public cert file not found', e.message)

        settings_info['security']['signMetadata'] = 'invalid_value'
        settings = OneLogin_Saml2_Settings(settings_info)
        try:
            settings.get_sp_metadata()
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Invalid Setting: signMetadata value of the sp is not valid', e.message)

    def testValidateMetadata(self):
        """
        Tests the validateMetadata method of the OneLogin_Saml2_Settings
        Case valid metadata
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        metadata = settings.get_sp_metadata()
        self.assertEqual(len(settings.validate_metadata(metadata)), 0)

        xml = self.file_contents(join(self.data_path, 'metadata', 'metadata_settings1.xml'))
        self.assertEqual(len(settings.validate_metadata(xml)), 0)

        xml_2 = '<xml>invalid</xml>'
        self.assertIn('invalid_xml', settings.validate_metadata(xml_2))

        xml_3 = self.file_contents(join(self.data_path, 'metadata', 'entities_metadata.xml'))
        self.assertIn('noEntityDescriptor_xml', settings.validate_metadata(xml_3))

        xml_4 = self.file_contents(join(self.data_path, 'metadata', 'idp_metadata.xml'))
        self.assertIn('onlySPSSODescriptor_allowed_xml', settings.validate_metadata(xml_4))

        xml_5 = self.file_contents(join(self.data_path, 'metadata', 'no_expiration_mark_metadata.xml'))
        self.assertEqual(len(settings.validate_metadata(xml_5)), 0)

    def testValidateMetadataExpired(self):
        """
        Tests the validateMetadata method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        metadata = self.file_contents(join(self.data_path, 'metadata', 'expired_metadata_settings1.xml'))
        errors = settings.validate_metadata(metadata)
        self.assertNotEqual(len(metadata), 0)
        self.assertIn('expired_xml', errors)

    def testValidateMetadataNoXML(self):
        """
        Tests the validateMetadata method of the OneLogin_Saml2_Settings
        Case no metadata
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        metadata = ''
        try:
            errors = settings.validate_metadata(metadata)
            self.assertTrue(False)
        except Exception as e:
            self.assertIn('Empty string supplied as input', e.message)

        metadata = '<no xml>'
        errors = settings.validate_metadata(metadata)

        self.assertNotEqual(len(errors), 0)
        self.assertIn('unloaded_xml', errors)

    def testValidateMetadataNoEntity(self):
        """
        Tests the validateMetadata method of the OneLogin_Saml2_Settings
        Case invalid xml metadata
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())
        metadata = self.file_contents(join(self.data_path, 'metadata', 'noentity_metadata_settings1.xml'))
        errors = settings.validate_metadata(metadata)
        self.assertNotEqual(len(metadata), 0)
        self.assertIn('invalid_xml', errors)

    def testGetIdPData(self):
        """
        Tests the getIdPData method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        idp_data = settings.get_idp_data()
        self.assertNotEqual(len(idp_data), 0)
        self.assertIn('entityId', idp_data)
        self.assertIn('singleSignOnService', idp_data)
        self.assertIn('singleLogoutService', idp_data)
        self.assertIn('NameIDPolicyFormat', idp_data)
        self.assertIn('NameIDPolicyAllowCreate', idp_data)
        self.assertIn('x509cert', idp_data)

        self.assertEqual('http://idp.example.com/', idp_data['entityId'])
        self.assertEqual('http://idp.example.com/SSOService.php', idp_data['singleSignOnService']['url'])
        self.assertEqual('http://idp.example.com/SingleLogoutService.php', idp_data['singleLogoutService']['url'])
        self.assertEqual('urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified', idp_data['NameIDPolicyFormat'])
        self.assertTrue(idp_data['NameIDPolicyAllowCreate'])

        x509cert = 'MIICgTCCAeoCCQCbOlrWDdX7FTANBgkqhkiG9w0BAQUFADCBhDELMAkGA1UEBhMCTk8xGDAWBgNVBAgTD0FuZHJlYXMgU29sYmVyZzEMMAoGA1UEBxMDRm9vMRAwDgYDVQQKEwdVTklORVRUMRgwFgYDVQQDEw9mZWlkZS5lcmxhbmcubm8xITAfBgkqhkiG9w0BCQEWEmFuZHJlYXNAdW5pbmV0dC5ubzAeFw0wNzA2MTUxMjAxMzVaFw0wNzA4MTQxMjAxMzVaMIGEMQswCQYDVQQGEwJOTzEYMBYGA1UECBMPQW5kcmVhcyBTb2xiZXJnMQwwCgYDVQQHEwNGb28xEDAOBgNVBAoTB1VOSU5FVFQxGDAWBgNVBAMTD2ZlaWRlLmVybGFuZy5ubzEhMB8GCSqGSIb3DQEJARYSYW5kcmVhc0B1bmluZXR0Lm5vMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDivbhR7P516x/S3BqKxupQe0LONoliupiBOesCO3SHbDrl3+q9IbfnfmE04rNuMcPsIxB161TdDpIesLCn7c8aPHISKOtPlAeTZSnb8QAu7aRjZq3+PbrP5uW3TcfCGPtKTytHOge/OlJbo078dVhXQ14d1EDwXJW1rRXuUt4C8QIDAQABMA0GCSqGSIb3DQEBBQUAA4GBACDVfp86HObqY+e8BUoWQ9+VMQx1ASDohBjwOsg2WykUqRXF+dLfcUH9dWR63CtZIKFDbStNomPnQz7nbK+onygwBspVEbnHuUihZq3ZUdmumQqCw4Uvs/1Uvq3orOo/WJVhTyvLgFVK2QarQ4/67OZfHd7R+POBXhophSMv1ZOo'
        formated_x509_cert = OneLogin_Saml2_Utils.format_cert(x509cert)
        self.assertEqual(formated_x509_cert, idp_data['x509cert'])

    def testGetSPData(self):
        """
        Tests the getSPData method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        sp_data = settings.get_sp_data()
        self.assertNotEqual(len(sp_data), 0)
        self.assertIn('entityId', sp_data)
        self.assertIn('assertionConsumerService', sp_data)
        self.assertIn('singleLogoutService', sp_data)
        self.assertIn('NameIDFormats', sp_data)

        self.assertEqual('http://stuff.com/endpoints/metadata.php', sp_data['entityId'])
        self.assertEqual('http://stuff.com/endpoints/endpoints/acs.php', sp_data['assertionConsumerService']['url'])
        self.assertEqual('http://stuff.com/endpoints/endpoints/sls.php', sp_data['singleLogoutService']['url'])
        self.assertEqual(['urn:oasis:names:tc:SAML:2.0:nameid-format:unspecified'], sp_data['NameIDFormats'])

    def testGetSecurityData(self):
        """
        Tests the getSecurityData method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        security = settings.get_security_data()
        self.assertNotEqual(len(security), 0)
        self.assertIn('nameIdEncrypted', security)
        self.assertIn('authnRequestsSigned', security)
        self.assertIn('logoutRequestSigned', security)
        self.assertIn('logoutResponseSigned', security)
        self.assertIn('signMetadata', security)
        self.assertIn('wantMessagesSigned', security)
        self.assertIn('wantAssertionsSigned', security)
        self.assertIn('wantNameIdEncrypted', security)

    def testGetContacts(self):
        """
        Tests the getContacts method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        contacts = settings.get_contacts()
        self.assertNotEqual(len(contacts), 0)
        self.assertEqual('technical_name', contacts['technical']['givenName'])
        self.assertEqual('technical@example.com', contacts['technical']['emailAddress'])
        self.assertEqual('support_name', contacts['support']['givenName'])
        self.assertEqual('support@example.com', contacts['support']['emailAddress'])

    def testGetOrganization(self):
        """
        Tests the getOrganization method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        organization = settings.get_organization()
        self.assertNotEqual(len(organization), 0)
        self.assertEqual('sp_test', organization['en-US']['name'])
        self.assertEqual('SP test', organization['en-US']['displayname'])
        self.assertEqual('http://sp.example.com', organization['en-US']['url'])

    def testSetStrict(self):
        """
        Tests the setStrict method of the OneLogin_Saml2_Settings
        """
        settings = OneLogin_Saml2_Settings(self.loadSettingsJSON())

        self.assertFalse(settings.is_strict())

        settings.set_strict(True)
        self.assertTrue(settings.is_strict())

        settings.set_strict(False)
        self.assertFalse(settings.is_strict())

        try:
            settings.set_strict('a')
            1 / 0
        except Exception as e:
            self.assertIsInstance(e, AssertionError)

    def testIsStrict(self):
        """
        Tests the isStrict method of the OneLogin_Saml2_Settings
        """
        settings_info = self.loadSettingsJSON()
        del settings_info['strict']

        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertFalse(settings.is_strict())

        settings_info['strict'] = False
        settings_2 = OneLogin_Saml2_Settings(settings_info)
        self.assertFalse(settings_2.is_strict())

        settings_info['strict'] = True
        settings_3 = OneLogin_Saml2_Settings(settings_info)
        self.assertTrue(settings_3.is_strict())

    def testIsDebugActive(self):
        """
        Tests the isDebugActive method of the OneLogin_Saml2_Settings
        """
        settings_info = self.loadSettingsJSON()
        del settings_info['debug']

        settings = OneLogin_Saml2_Settings(settings_info)
        self.assertFalse(settings.is_debug_active())

        settings_info['debug'] = False
        settings_2 = OneLogin_Saml2_Settings(settings_info)
        self.assertFalse(settings_2.is_debug_active())

        settings_info['debug'] = True
        settings_3 = OneLogin_Saml2_Settings(settings_info)
        self.assertTrue(settings_3.is_debug_active())
