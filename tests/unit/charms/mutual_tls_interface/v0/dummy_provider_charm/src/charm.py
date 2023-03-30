# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

from ops.charm import CharmBase
from ops.main import main

from lib.charms.mutual_tls_interface.v0.mutual_tls import MutualTLSProvides


class DummyMutualTLSProviderCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.mutual_tls = MutualTLSProvides(self, "certificates")


if __name__ == "__main__":
    main(DummyMutualTLSProviderCharm)
