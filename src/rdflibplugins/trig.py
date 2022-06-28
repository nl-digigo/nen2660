"""Disables auto-generated QNames, for prettier TriG output.

This prevents generation of `prefix ns1: <https:// ... >` etc. declarations in
the TriG file header.
"""
# COPYRIGHT 2022 Redmer Kronemeijer <redmer.kronemeijer@crow.nl>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from rdflib.serializer import Serializer
from rdflib.plugins.serializers.trig import TrigSerializer
from rdflib.plugin import register


class CrowTrigSerializer(TrigSerializer):
    def getQName(self, uri, gen_prefix=False):
        return super().getQName(uri, gen_prefix=gen_prefix)


register("trig-ns", Serializer, "rdflibplugins.trig", "CrowTrigSerializer")
