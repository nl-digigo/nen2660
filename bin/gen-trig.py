#!/usr/bin/env python3
"""Generate concatenated TriG files."""
# COPYRIGHT 2021 Redmer Kronemeijer <redmer.kronemeijer@crow.nl>
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


from rdflib import Dataset, Graph
from pathlib import Path

from rdflib.namespace import OWL, RDF, SKOS

# In rdflib/plugins/serializers/turtle.py
#   CHANGE def getQName(self, uri, gen_prefix=True):
#   INTO def getQName(self, uri, gen_prefix=False):

import rdflibplugins.trig


def OWL_Ontology_base(input_file):
    """Get first subject of `rdf:type owl:Ontology`"""
    g = Graph().parse(str(input_file), format=input_file.suffix[1:])

    for subject in g.subjects(predicate=RDF.type, object=OWL.Ontology):
        return subject

    for subject in g.subjects(predicate=RDF.type, object=SKOS.ConceptScheme):
        return subject


def bind(g: Graph):
    g.bind("xsd", "http://www.w3.org/2001/XMLSchema#")


def generate_quad_files():
    trig = Dataset()

    for input_file in Path("./data/").glob("*.ttl"):
        graph_uri = OWL_Ontology_base(input_file)

        g = trig.graph(graph_uri)
        g.parse(str(input_file), format=input_file.suffix[1:])

    bind(trig)
    trig.serialize("./data/concat/nen2660.trig", format="trig-ns", encoding="utf-8")


def generate_triple_files():
    g = Graph()

    for input_file in Path("./data/").glob("*.ttl"):
        g.parse(str(input_file), format=input_file.suffix[1:])

    g.serialize("./data/concat/nen2660.rdf", format="xml", encoding="utf-8")
    g.serialize("./data/concat/nen2660.ttl", format="ttl", encoding="utf-8")
    g.serialize("./data/concat/nen2660.json", format="json-ld", encoding="utf-8")


def generate_lov_files():
    g = Graph()

    for input_file in Path("./data/").glob("*.ttl"):
        g.parse(str(input_file), format=input_file.suffix[1:])

    g.parse("./data/metadata/lov.ttl", format="ttl")

    g.serialize(
        "./data/concat/nen2660-lov-metadata.ttl", format="ttl", encoding="utf-8"
    )


if __name__ == "__main__":
    generate_quad_files()
    generate_triple_files()
    generate_lov_files()
