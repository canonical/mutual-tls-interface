"""TODO: Add a proper docstring here.

This is a placeholder docstring for this charm library. Docstrings are
presented on Charmhub and updated whenever you push a new version of the
library.

Complete documentation about creating and documenting libraries can be found
in the SDK docs at https://juju.is/docs/sdk/libraries.

See `charmcraft publish-lib` and `charmcraft fetch-lib` for details of how to
share and consume charm libraries. They serve to enhance collaboration
between charmers. Use a charmer's libraries for classes that handle
integration with their charm.

Bear in mind that new revisions of the different major API versions (v0, v1,
v2 etc) are maintained independently.  You can continue to update v0 and v1
after you have pushed v3.

Markdown is supported, following the CommonMark specification.
"""


import json
import logging
from typing import List

from jsonschema import exceptions, validate  # type: ignore[import]
from ops.charm import (
    CharmBase,
    CharmEvents,
    RelationChangedEvent,
)
from ops.framework import EventBase, EventSource, Handle, Object

# The unique Charmhub library identifier, never change it
LIBID = "b24dab3c7b464669a7710806defe34d4"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


logger = logging.getLogger(__name__)


PROVIDER_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "https://canonical.github.io/charm-relation-interfaces/interfaces/mutual_tls/schemas/provider.json",  # noqa: E501
    "type": "object",
    "title": "`mutual_tls` provider schema",
    "description": "The `mutual_tls` root schema comprises the entire provider application databag for this interface.",  # noqa: E501
    "default": {},
    "examples": [
        {
            "certificate": "-----BEGIN CERTIFICATE-----\nMIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL\nBQAwIDELMAkGA1UEBhMCVVMxETAPBgNVBAMMCHdoYXRldmVyMB4XDTIzMDMyNDE4\nNDMxOVoXDTI0MDMyMzE4NDMxOVowPDELMAkGA1UEAwwCb2sxLTArBgNVBC0MJGUw\nNjVmMWI3LTE2OWEtNDE5YS1iNmQyLTc3OWJkOGM4NzIwNjCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBAK42ixoklDH5K5i1NxXo/AFACDa956pE5RA57wlC\nBfgUYaIDRmv7TUVJh6zoMZSD6wjSZl3QgP7UTTZeHbvs3QE9HUwEkH1Lo3a8vD3z\neqsE2vSnOkpWWnPbfxiQyrTm77/LAWBt7lRLRLdfL6WcucD3wsGqm58sWXM3HG0f\nSN7PHCZUFqU6MpkHw8DiKmht5hBgWG+Vq3Zw8MNaqpwb/NgST3yYdcZwb58G2FTS\nZvDSdUfRmD/mY7TpciYV8EFylXNNFkth8oGNLunR9adgZ+9IunfRKj1a7S5GSwXU\nAZDaojw+8k5i3ikztsWH11wAVCiLj/3euIqq95z8xGycnKcCAwEAATANBgkqhkiG\n9w0BAQsFAAOCAQEAWMvcaozgBrZ/MAxzTJmp5gZyLxmMNV6iT9dcqbwzDtDtBvA/\n46ux6ytAQ+A7Bd3AubvozwCr1Id6g66ae0blWYRRZmF8fDdX/SBjIUkv7u9A3NVQ\nXN9gsEvK9pdpfN4ZiflfGSLdhM1STHycLmhG6H5s7HklbukMRhQi+ejbSzm/wiw1\nipcxuKhSUIVNkTLusN5b+HE2gwF1fn0K0z5jWABy08huLgbaEKXJEx5/FKLZGJga\nfpIzAdf25kMTu3gggseaAmzyX3AtT1i8A8nqYfe8fnnVMkvud89kq5jErv/hlMC9\n49g5yWQR2jilYYM3j9BHDuB+Rs+YS5BCep1JnQ==\n-----END CERTIFICATE-----\n",  # noqa: E501
            "ca": "-----BEGIN CERTIFICATE-----\nMIIC6DCCAdCgAwIBAgIUdiBwE/CtaBXJl3MArjZen6Y8kigwDQYJKoZIhvcNAQEL\nBQAwIDELMAkGA1UEBhMCVVMxETAPBgNVBAMMCHdoYXRldmVyMB4XDTIzMDMyNDE4\nNDg1OVoXDTI0MDMyMzE4NDg1OVowPDELMAkGA1UEAwwCb2sxLTArBgNVBC0MJDEw\nMDdjNDBhLWUwYzMtNDVlOS05YTAxLTVlYjY0NWQ0ZmEyZDCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANOnUl6JDlXpLMRr/PxgtfE/E5Yk6E/TkPkPL/Kk\ntUGjEi42XZDg9zn3U6cjTDYu+rfKY2jiitfsduW6DQIkEpz3AvbuCMbbgnFpcjsB\nYysLSMTmuz/AVPrfnea/tQTALcONCSy1VhAjGSr81ZRSMB4khl9StSauZrbkpJ1P\nshqkFSUyAi31mKrnXz0Es/v0Yi0FzAlgWrZ4u1Ld+Bo2Xz7oK4mHf7/93Jc+tEaM\nIqG6ocD0q8bjPp0tlSxftVADNUzWlZfM6fue5EXzOsKqyDrxYOSchfU9dNzKsaBX\nkxbHEeSUPJeYYj7aVPEfAs/tlUGsoXQvwWfRie8grp2BoLECAwEAATANBgkqhkiG\n9w0BAQsFAAOCAQEACZARBpHYH6Gr2a1ka0mCWfBmOZqfDVan9rsI5TCThoylmaXW\nquEiZ2LObI+5faPzxSBhr9TjJlQamsd4ywout7pHKN8ZGqrCMRJ1jJbUfobu1n2k\nUOsY4+jzV1IRBXJzj64fLal4QhUNv341lAer6Vz3cAyRk7CK89b/DEY0x+jVpyZT\n1osx9JtsOmkDTgvdStGzq5kPKWOfjwHkmKQaZXliCgqbhzcCERppp1s/sX6K7nIh\n4lWiEmzUSD3Hngk51KGWlpZszO5KQ4cSZ3HUt/prg+tt0ROC3pY61k+m5dDUa9M8\nRtMI6iTjzSj/UV8DiAx0yeM+bKoy4jGeXmaL3g==\n-----END CERTIFICATE-----\n",  # noqa: E501
            "chain": [
                "-----BEGIN CERTIFICATE-----\nMIIC6DCCAdCgAwIBAgIUW42TU9LSjEZLMCclWrvSwAsgRtcwDQYJKoZIhvcNAQEL\nBQAwIDELMAkGA1UEBhMCVVMxETAPBgNVBAMMCHdoYXRldmVyMB4XDTIzMDMyNDE4\nNDMxOVoXDTI0MDMyMzE4NDMxOVowPDELMAkGA1UEAwwCb2sxLTArBgNVBC0MJGUw\nNjVmMWI3LTE2OWEtNDE5YS1iNmQyLTc3OWJkOGM4NzIwNjCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBAK42ixoklDH5K5i1NxXo/AFACDa956pE5RA57wlC\nBfgUYaIDRmv7TUVJh6zoMZSD6wjSZl3QgP7UTTZeHbvs3QE9HUwEkH1Lo3a8vD3z\neqsE2vSnOkpWWnPbfxiQyrTm77/LAWBt7lRLRLdfL6WcucD3wsGqm58sWXM3HG0f\nSN7PHCZUFqU6MpkHw8DiKmht5hBgWG+Vq3Zw8MNaqpwb/NgST3yYdcZwb58G2FTS\nZvDSdUfRmD/mY7TpciYV8EFylXNNFkth8oGNLunR9adgZ+9IunfRKj1a7S5GSwXU\nAZDaojw+8k5i3ikztsWH11wAVCiLj/3euIqq95z8xGycnKcCAwEAATANBgkqhkiG\n9w0BAQsFAAOCAQEAWMvcaozgBrZ/MAxzTJmp5gZyLxmMNV6iT9dcqbwzDtDtBvA/\n46ux6ytAQ+A7Bd3AubvozwCr1Id6g66ae0blWYRRZmF8fDdX/SBjIUkv7u9A3NVQ\nXN9gsEvK9pdpfN4ZiflfGSLdhM1STHycLmhG6H5s7HklbukMRhQi+ejbSzm/wiw1\nipcxuKhSUIVNkTLusN5b+HE2gwF1fn0K0z5jWABy08huLgbaEKXJEx5/FKLZGJga\nfpIzAdf25kMTu3gggseaAmzyX3AtT1i8A8nqYfe8fnnVMkvud89kq5jErv/hlMC9\n49g5yWQR2jilYYM3j9BHDuB+Rs+YS5BCep1JnQ==\n-----END CERTIFICATE-----\n",  # noqa: E501
                "-----BEGIN CERTIFICATE-----\nMIIC6DCCAdCgAwIBAgIUdiBwE/CtaBXJl3MArjZen6Y8kigwDQYJKoZIhvcNAQEL\nBQAwIDELMAkGA1UEBhMCVVMxETAPBgNVBAMMCHdoYXRldmVyMB4XDTIzMDMyNDE4\nNDg1OVoXDTI0MDMyMzE4NDg1OVowPDELMAkGA1UEAwwCb2sxLTArBgNVBC0MJDEw\nMDdjNDBhLWUwYzMtNDVlOS05YTAxLTVlYjY0NWQ0ZmEyZDCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANOnUl6JDlXpLMRr/PxgtfE/E5Yk6E/TkPkPL/Kk\ntUGjEi42XZDg9zn3U6cjTDYu+rfKY2jiitfsduW6DQIkEpz3AvbuCMbbgnFpcjsB\nYysLSMTmuz/AVPrfnea/tQTALcONCSy1VhAjGSr81ZRSMB4khl9StSauZrbkpJ1P\nshqkFSUyAi31mKrnXz0Es/v0Yi0FzAlgWrZ4u1Ld+Bo2Xz7oK4mHf7/93Jc+tEaM\nIqG6ocD0q8bjPp0tlSxftVADNUzWlZfM6fue5EXzOsKqyDrxYOSchfU9dNzKsaBX\nkxbHEeSUPJeYYj7aVPEfAs/tlUGsoXQvwWfRie8grp2BoLECAwEAATANBgkqhkiG\n9w0BAQsFAAOCAQEACZARBpHYH6Gr2a1ka0mCWfBmOZqfDVan9rsI5TCThoylmaXW\nquEiZ2LObI+5faPzxSBhr9TjJlQamsd4ywout7pHKN8ZGqrCMRJ1jJbUfobu1n2k\nUOsY4+jzV1IRBXJzj64fLal4QhUNv341lAer6Vz3cAyRk7CK89b/DEY0x+jVpyZT\n1osx9JtsOmkDTgvdStGzq5kPKWOfjwHkmKQaZXliCgqbhzcCERppp1s/sX6K7nIh\n4lWiEmzUSD3Hngk51KGWlpZszO5KQ4cSZ3HUt/prg+tt0ROC3pY61k+m5dDUa9M8\nRtMI6iTjzSj/UV8DiAx0yeM+bKoy4jGeXmaL3g==\n-----END CERTIFICATE-----\n",  # noqa: E501
            ],
        }
    ],
    "required": ["certificate"],
    "properties": {
        "certificate": {
            "$id": "#/properties/certificate",
            "type": "string",
            "title": "Public TLS certificate",
            "description": "Public TLS certificate",
        },
        "ca": {
            "$id": "#/properties/ca",
            "type": "string",
            "title": "CA public TLS certificate",
            "description": "CA Public TLS certificate",
        },
        "chain": {
            "$id": "#/properties/chain",
            "type": "array",
            "items": {"type": "string", "$id": "#/properties/chain/items"},
            "title": "CA public TLS certificate chain",
            "description": "CA public TLS certificate chain",
        },
    },
    "additionalProperties": True,
}


class CertificateAvailableEvent(EventBase):
    """Charm Event triggered when a TLS certificate is available."""

    def __init__(
        self,
        handle: Handle,
        certificate: str,
        ca: str,
        chain: List[str],
    ):
        super().__init__(handle)
        self.certificate = certificate
        self.ca = ca
        self.chain = chain

    def snapshot(self) -> dict:
        """Return snapshot."""
        return {
            "certificate": self.certificate,
            "ca": self.ca,
            "chain": self.chain,
        }

    def restore(self, snapshot: dict):
        """Restores snapshot."""
        self.certificate = snapshot["certificate"]
        self.ca = snapshot["ca"]
        self.chain = snapshot["chain"]


def _load_relation_data(raw_relation_data: dict) -> dict:
    """Load relation data from the relation data bag.

    Json loads all data.

    Args:
        raw_relation_data: Relation data from the databag

    Returns:
        dict: Relation data in dict format.
    """
    certificate_data = {}
    for key in raw_relation_data:
        try:
            certificate_data[key] = json.loads(raw_relation_data[key])
        except (json.decoder.JSONDecodeError, TypeError):
            certificate_data[key] = raw_relation_data[key]
    return certificate_data


class MutualTLSRequirerCharmEvents(CharmEvents):
    """List of events that the Mutual TLS requirer charm can leverage."""

    certificate_available = EventSource(CertificateAvailableEvent)


class MutualTLSProvides(Object):
    """Mutual TLS provider class."""

    def __init__(self, charm: CharmBase, relationship_name: str):
        super().__init__(charm, relationship_name)
        self.charm = charm
        self.relationship_name = relationship_name

    def set_certificate(
        self,
        certificate: str,
        ca: str,
        chain: List[str],
        relation_id: int = None,
    ) -> None:
        """Add certificates to relation data.

        Args:
            certificate (str): Certificate
            ca (str): CA Certificate
            chain (list): CA Chain
            relation_id (int): Juju relation ID

        Returns:
            None
        """
        relation = self.model.get_relation(
            relation_name=self.relationship_name,
            relation_id=relation_id,
        )
        relation.data[self.model.unit]["certificate"] = certificate
        relation.data[self.model.unit]["ca"] = ca
        relation.data[self.model.unit]["chain"] = json.dumps(chain)

    def remove_certificate(self, relation_id: int = None) -> None:
        """Remove a given certificate from relation data.

        Args:
            relation_id (int): Relation ID

        Returns:
            None
        """
        relation = self.model.get_relation(
            relation_name=self.relationship_name,
            relation_id=relation_id,
        )
        relation.data[self.model.unit].pop("certificate")
        relation.data[self.model.unit].pop("ca")
        relation.data[self.model.unit].pop("chain")


class MutualTLSRequires(Object):
    """TLS certificates requirer class to be instantiated by TLS certificates requirers."""

    on = MutualTLSRequirerCharmEvents()

    def __init__(
        self,
        charm: CharmBase,
        relationship_name: str,
    ):
        """Generates/use private key and observes relation changed event.

        Args:
            charm: Charm object
            relationship_name: Juju relation name
        """
        super().__init__(charm, relationship_name)
        self.relationship_name = relationship_name
        self.charm = charm
        self.framework.observe(
            charm.on[relationship_name].relation_changed, self._on_relation_changed
        )

    @staticmethod
    def _relation_data_is_valid(certificates_data: dict) -> bool:
        """Return whether relation data is valid based on json schema.

        Args:
            certificates_data: Certificate data in dict format.

        Returns:
            bool: Whether relation data is valid.
        """
        try:
            validate(instance=certificates_data, schema=PROVIDER_JSON_SCHEMA)
            return True
        except exceptions.ValidationError:
            return False

    def _on_relation_changed(self, event: RelationChangedEvent) -> None:
        """Emit certificate available event.

        Args:
            event: Juju event

        Returns:
            None
        """
        relation = self.model.get_relation(self.relationship_name, relation_id=event.relation.id)
        if not relation:
            logger.warning(f"No relation: {self.relationship_name}")
            return
        if not relation.app:
            logger.warning(f"No remote app in relation: {self.relationship_name}")
            return
        provider_relation_data = _load_relation_data(relation.data[relation.app])
        if not self._relation_data_is_valid(provider_relation_data):
            logger.warning(
                f"Provider relation data did not pass JSON Schema validation: "
                f"{event.relation.data[relation.app]}"
            )
            return
        self.on.certificate_available.emit(
            certificate=provider_relation_data["certificate"],
            ca=provider_relation_data["ca"],
            chain=provider_relation_data["chain"],
        )