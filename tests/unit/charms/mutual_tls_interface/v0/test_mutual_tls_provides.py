# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

import json
import unittest

from ops import testing

from tests.unit.charms.mutual_tls_interface.v0.dummy_provider_charm.src.charm import (
    DummyMutualTLSProviderCharm,
)

BASE_LIB_DIR = "lib.charms.mutual_tls_interface.v0.mutual_tls"


class TestMutualTLSProvides(unittest.TestCase):
    def setUp(self):
        self.unit_name = "mutual-tls-interface-provider/0"
        self.harness = testing.Harness(DummyMutualTLSProviderCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def create_mutual_tls_relation(self) -> int:
        relation_name = "certificates"
        remote_app_name = "mutual-tls-requirer"
        relation_id = self.harness.add_relation(
            relation_name=relation_name,
            remote_app=remote_app_name,
        )
        return relation_id

    def test_given_mutual_tls_relation_exists_when_set_certificate_then_certificate_added_to_relation_data(  # noqa: E501
        self,
    ):
        relation_id = self.create_mutual_tls_relation()

        certificate = "whatever cert"
        ca = "whatever ca"
        chain = ["whatever cert 1", "whatever cert 2"]

        self.harness.charm.mutual_tls.set_certificate(
            certificate=certificate, ca=ca, chain=chain, relation_id=relation_id
        )

        relation_data = self.harness.get_relation_data(
            app_or_unit="mutual-tls-interface-provider/0",
            relation_id=relation_id,
        )
        self.assertEqual(relation_data["certificate"], certificate)
        self.assertEqual(relation_data["ca"], ca)
        self.assertEqual(relation_data["chain"], json.dumps(chain))

    def test_given_relation_id_not_provided_and_mutual_tls_relation_exists_when_set_certificate_then_certificate_added_to_relation_data(  # noqa: E501
        self,
    ):
        relation_id = self.create_mutual_tls_relation()

        certificate = "whatever cert"
        ca = "whatever ca"
        chain = ["whatever cert 1", "whatever cert 2"]

        self.harness.charm.mutual_tls.set_certificate(certificate=certificate, ca=ca, chain=chain)

        relation_data = self.harness.get_relation_data(
            app_or_unit="mutual-tls-interface-provider/0",
            relation_id=relation_id,
        )
        self.assertEqual(relation_data["certificate"], certificate)
        self.assertEqual(relation_data["ca"], ca)
        self.assertEqual(relation_data["chain"], json.dumps(chain))

    def test_given_no_mutual_tls_relation_when_set_certificate_then_runtime_error_is_raised(self):
        certificate = "whatever cert"
        ca = "whatever ca"
        chain = ["whatever cert 1", "whatever cert 2"]

        with self.assertRaises(RuntimeError):
            self.harness.charm.mutual_tls.set_certificate(
                certificate=certificate, ca=ca, chain=chain
            )

    def test_given_mutual_tls_relation_exists_when_remove_certificate_then_certificate_removed_from_relation_data(  # noqa: E501
        self,
    ):
        relation_id = self.create_mutual_tls_relation()
        relation_data = {
            "certificate": "whatever cert",
            "ca": "whatever ca",
            "chain": json.dumps(["cert 1", "cert 2"]),
        }
        self.harness.update_relation_data(
            relation_id=relation_id,
            key_values=relation_data,
            app_or_unit="mutual-tls-interface-provider/0",
        )

        self.harness.charm.mutual_tls.remove_certificate(relation_id=relation_id)

        relation_data = self.harness.get_relation_data(
            app_or_unit="mutual-tls-interface-provider/0",
            relation_id=relation_id,
        )
        assert "certificate" not in relation_data
        assert "ca" not in relation_data
        assert "chain" not in relation_data

    def test_given_only_certificate_in_relation_data_when_remove_certificate_then_certificate_removed_from_relation_data(  # noqa: E501
        self,
    ):
        relation_id = self.create_mutual_tls_relation()
        relation_data = {
            "certificate": "whatever cert",
        }
        self.harness.update_relation_data(
            relation_id=relation_id,
            key_values=relation_data,
            app_or_unit="mutual-tls-interface-provider/0",
        )

        self.harness.charm.mutual_tls.remove_certificate(relation_id=relation_id)

        relation_data = self.harness.get_relation_data(
            app_or_unit="mutual-tls-interface-provider/0",
            relation_id=relation_id,
        )
        assert "certificate" not in relation_data

    def test_given_mutual_tls_relation_exists_and_id_not_provided_when_remove_certificate_then_certificate_removed_from_relation_data(  # noqa: E501
        self,
    ):
        relation_id = self.create_mutual_tls_relation()
        relation_data = {
            "certificate": "whatever cert",
            "ca": "whatever ca",
            "chain": json.dumps(["cert 1", "cert 2"]),
        }
        self.harness.update_relation_data(
            relation_id=relation_id,
            key_values=relation_data,
            app_or_unit="mutual-tls-interface-provider/0",
        )

        self.harness.charm.mutual_tls.remove_certificate()

        relation_data = self.harness.get_relation_data(
            app_or_unit="mutual-tls-interface-provider/0",
            relation_id=relation_id,
        )
        assert "certificate" not in relation_data
        assert "ca" not in relation_data
        assert "chain" not in relation_data

    def test_given_mutual_tls_relation_doesnt_exist_when_remove_then_log_is_emitted(self):
        with self.assertLogs(BASE_LIB_DIR, level="WARNING") as log:
            self.harness.charm.mutual_tls.remove_certificate()

        assert "Can't remove certificate - Non-existent relation 'certificates'" in log.output[0]

    def test_given_no_data_in_mutual_tls_relation_when_remove_certificate_then_log_is_emitted(  # noqa: E501
        self,
    ):
        self.create_mutual_tls_relation()

        with self.assertLogs(BASE_LIB_DIR, level="WARNING") as log:
            self.harness.charm.mutual_tls.remove_certificate()

        assert "Can't remove certificate - No certificate in relation data" in log.output[0]
