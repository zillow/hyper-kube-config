import os
import sys
from requests import Request
import unittest

from click.testing import CliRunner
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(TEST_DIR, '..'))
spec = spec_from_loader(
    "kubectl-hyperkube",
    SourceFileLoader("kubectl-hyperkube", "./cli/kubectl-hyperkube"))
kubectl_hyperkube = module_from_spec(spec)
spec.loader.exec_module(kubectl_hyperkube)


class TestHyperKubeApplication(unittest.TestCase):
    """Test hyperkube application config and functions"""

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(
            kubectl_hyperkube.cli,
            ['--config', 'config_test_hyperkube.yaml', '--help'])
        assert result.exit_code == 0

    def test_load_app_config(self):
        config = kubectl_hyperkube._load_config(
            'tests/config_test_hyperkube.yaml')
        assert config['stage'] == 'dev'
        assert config['x_api_key'] == (
            '1234567891abcfedrtas123454321Z1234567891')
        assert config['aws_profile'] == 'default'
        assert config['region'] == 'us-west-2'

    def test_signature_generation_for_iam(self):
        """
        Test the dictionary returned by AWSProfileAuth which is used
        in `auth` input to request sent to AWS API Gateway.
        This dict should contain signature values used by AWS API
        Gateway Resource Policy to determine access to API from HTTP
        request. This test just confirms the override functionality
        we needed to create to support AWS_PROFILE. By default,
        aws_requests_auth doesn't support this directly.
        """
        # Mock request object, needed for signature generation
        r = Request(
            'POST',
            "https://123456780.execute-api.us-west-2.amazonaws.com",
            json={'key': 'value'})
        r.prepare()
        r.body = "test-text"

        sig_generation_without_profile = kubectl_hyperkube.AWSProfileAuth(
            aws_host="https://123456780.execute-api.us-west-2.amazonaws.com",
            aws_region='us-west-2',
            aws_service='execute-api',
            profile=None)

        sig_without_profile_result = (
            sig_generation_without_profile.get_aws_request_headers(
                r,
                aws_access_key="fffasdfdfadadsfdkaf101010",
                aws_secret_access_key="akdsfjasdfwiqer;s123k122",
                aws_token="testingtokenaklzaner")
        )
        assert "Credential=fffasdfdfadadsfdkaf101010" in (
            sig_without_profile_result['Authorization']
        )
        assert "us-west-2/execute-api/aws4_request" in (
            sig_without_profile_result['Authorization']
        )
        assert (
            "SignedHeaders=host;x-amz-date;x-amz-security-token" in (
                sig_without_profile_result['Authorization'])
        )
        assert (
            "b18939c1891ba923a4d46ccf146612094490300d22e436bf5a5d6d46d99e4225" in ( # noqa
                sig_without_profile_result['x-amz-content-sha256'])
        )
        assert sig_without_profile_result['X-Amz-Security-Token'] == (
            "testingtokenaklzaner"
        )

        # requires ~/.aws/config to have a `[default]` profile
        sig_generation_with_profile = kubectl_hyperkube.AWSProfileAuth(
            aws_host="https://123456780.execute-api.us-west-2.amazonaws.com",
            aws_region='us-west-2',
            aws_service='execute-api',
            profile="default")

        sig_with_profile_result = (
            sig_generation_with_profile.get_aws_request_headers(
                r,
                aws_access_key="fffasdfdfadadsfdkaf102381",
                aws_secret_access_key="akdsfjasdfwiqer;sfkjk213",
                aws_token="testingtokenakldsfkja;")
        )
        assert "Credential=fffasdfdfadadsfdkaf102381" in (
            sig_with_profile_result['Authorization']
        )
        assert "us-west-2/execute-api/aws4_request" in (
            sig_with_profile_result['Authorization']
        )
        assert (
            "SignedHeaders=host;x-amz-date;x-amz-security-token" in (
                sig_with_profile_result['Authorization'])
        )
        assert (
            "b18939c1891ba923a4d46ccf146612094490300d22e436bf5a5d6d46d99e4225" in ( # noqa
                sig_with_profile_result['x-amz-content-sha256'])
        )
        assert sig_with_profile_result['X-Amz-Security-Token'] == (
            "testingtokenakldsfkja;"
        )
