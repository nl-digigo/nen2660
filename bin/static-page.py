#!/usr/bin/env python3
"""Generate static HTML pages from linked data files."""
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


import functools
from html import escape
from pathlib import Path
from typing import List, Tuple, Union

import yaml
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.graph import Dataset
from rdflib.namespace import RDF
from rdflib.paths import ZeroOrMore, evalPath

CONFIG = yaml.safe_load(open("_config.yaml"))
TypedSerialization = Tuple[str, str, str, str]


class MainRenderer:
    def alternative_serialization(self, graph: Dataset):
        """Save alternative serializations of the dataset."""

        def ttl(graph: Dataset) -> TypedSerialization:
            return (
                "Turtle",
                "text/turtle",
                "ttl",
                graph.serialize(format="trig", encoding="utf-8").decode("utf-8"),
            )

        def trig(graph: Dataset) -> TypedSerialization:
            return (
                "TriG",
                "application/trig",
                "trig",
                graph.serialize(format="trig", encoding="utf-8").decode("utf-8"),
            )

        def rdfxml(graph: Dataset) -> TypedSerialization:
            return (
                "RDF/XML",
                "application/rdf+xml",
                "xml",
                graph.serialize(format="pretty-xml", encoding="utf-8").decode("utf-8"),
            )

        def jsonld(graph: Dataset) -> TypedSerialization:
            return (
                "JSON-LD",
                "application/ld+json",
                "json",
                graph.serialize(format="json-ld", encoding="utf-8").decode("utf-8"),
            )

        serializations: TypedSerialization = [
            ttl(graph),
            trig(graph),
            rdfxml(graph),
            jsonld(graph),
        ]

        output = []

        for name, mime, ext, contents in serializations:
            output_path = f"./serializations/"
            Path(output_path).mkdir(parents=True, exist_ok=True)
            with open(f"./serializations/data.{ext}", "w+") as output_file:
                output_file.write(contents)

            output.append(
                f"""<a href='/serializations/data.{ext}' type='{mime}' rel='alternate'>{name}</a>"""
            )

        return f"""<p>Alternative serializations: {', '.join(output)}.</p>"""

    def render(self, graph: Dataset):

        html = ""
        html += f"""\n\n{self.alternative_serialization(graph)}\n\n"""
        return html


@functools.total_ordering
class OntologyConcept:
    sort_title: str

    def __init__(self, uri: URIRef):
        self.uri = uri
        self.isInList = False

    def __eq__(self, other):
        if not isinstance(other, OntologyConcept):
            return NotImplemented
        return self.sort_title == other.sort_title

    def __lt__(self, other):
        if not isinstance(other, OntologyConcept):
            return NotImplemented
        return self.sort_title < other.sort_title

    def title(self, uri: URIRef, *, base="") -> str:
        relative = str(self.uri).replace(base, "")
        return f"""<div id='{relative}' class='mv5'>
        <h2 class='f3'><a class='link dim underline-hover brand-dark-color ' href='{str(uri)}'>{ relative }</a>
        <span class='f6'>{ escape(uri.n3()) }</span></h2>\n\n"""

    def sort_contexts(self, contexts: List[URIRef]):
        """Sorts contexts based on _config.yaml/staticld_ghpages/graph_order."""
        ordered = CONFIG["staticld_ghpages"]["graph_order"]
        allowed = [str(fn).split("/")[-1] for fn in ordered]

        fn_context = [(str(c).split("/")[-1], c) for c in contexts]

        for filename in allowed:
            context = filter(lambda v: filename == v[0], fn_context)
            context = list(context)
            if not context:
                continue
            assert len(context) == 1
            yield URIRef(context[0][1])

    def render_BNode(
        self, res: Union[URIRef, BNode, Literal], /, context: URIRef, level: int
    ):
        """Renders a blank node"""
        ttl_desc = "[\n"
        for __, p, o, __ in sorted(self.g.quads((res, None, None, context))):
            p = self.render_resource(p, context=context, level=level + 1)
            o = self.render_resource(o, context=context, level=level + 1)
            ttl_desc += "  " * level + f"  { p } { o } ;\n"
        ttl_desc += "  " * level + "]"

        return "<span class='pre'>" + ttl_desc + "</span>"

    def render_Literal(
        self, res: Union[URIRef, BNode, Literal], /, context: URIRef, level: int
    ):
        """Renders a literal"""
        replacements = {
            "^^<http://www.w3.org/2001/XMLSchema#integer>": "^^xsd:integer",
            "^^<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>": "^^xsd:nonNegativeInteger",
        }
        value = res.n3()  # TODO: Replace w/ all registered namespaces
        for strin, strout in replacements.items():
            value = value.replace(strin, strout)
        return escape(value)

    def render_URIRef(
        self, res: Union[URIRef, BNode, Literal], /, context: URIRef, level: int
    ):
        linked_ns = CONFIG["staticld_ghpages"]["linked_ns"]
        if self.g.compute_qname(res)[0] not in linked_ns:
            return (
                f"<a class='link dim underline-hover black' href='{res.toPython()}'>"
                + self.g.qname(res)
                + "</a>"
            )
        return (
            f"<a class='link dim underline-hover brand-dark-color' href='{res.toPython()}'>"
            + self.g.qname(res)
            + "</a>"
        )

    def render_RDF_List(
        self, res: Union[URIRef, BNode, Literal], /, context: URIRef, level: int
    ):
        # rdf:rest*/rdf:first
        subItems = (RDF.rest * ZeroOrMore) / RDF.first
        items = evalPath(self.g, (res, subItems, None, context))

        ttl_desc = ""
        for ctx, obj in items:
            # ttl_desc += " " + self.render_resource(ctx, context=context,level=level)
            ttl_desc += " " + self.render_resource(obj, context=context, level=level)

        return f"({ttl_desc} )"

    def render_resource(
        self, res: Union[URIRef, BNode, Literal], /, context: URIRef, level: int
    ):
        if res == RDF.nil:
            return "()"

        if (res, RDF.first, None, context) in self.g:
            return self.render_RDF_List(res, context=context, level=level)

        if type(res) == URIRef:
            return self.render_URIRef(res, context=context, level=level)

        if type(res) == Literal:
            return self.render_Literal(res, context=context, level=level)

        if type(res) == BNode:
            return self.render_BNode(res, context=context, level=level)

        return escape(res.n3())

    def render_graph_resource(self, graph: URIRef):
        def contents():
            filename = self.g.compute_qname(graph)[-1]
            baseurl = CONFIG["baseurl"]
            yield "From file"
            yield f"<a class='link dim underline-hover blue' href='{baseurl}/data/{filename}'>"
            yield filename
            yield "</a>"

        return "\n".join(contents())

    def render_po_tr(self, uri: URIRef, /, context: URIRef, level: int) -> str:
        def contents():
            data_this_graph = self.g.quads((uri, None, None, context))

            for __, p, o, __ in sorted(data_this_graph):
                yield "<tr>"
                yield "<td class='w-third'>" + self.render_resource(
                    p, context=context, level=level
                ) + "</td>"
                css_class = "w-third" if level > 0 else "w-two-thirds"
                yield f"<td class='{css_class} overflow-auto'>" + self.render_resource(
                    o, context=context, level=level
                ) + "</td>"
                yield "</tr>"

        return "\n".join(contents())

    def po_table(self, uri: URIRef, /, header=True) -> str:
        def contents():
            data_across_graphs = self.g.quads((uri, None, None, None))
            contexts = map(lambda quad: quad[-1], data_across_graphs)
            contexts = set(contexts)

            for c in self.sort_contexts(contexts):
                if header:
                    yield "<table class='w-100 mv4 f6 dt--fixed'>"
                    yield """<colgroup>
                                <col width="33%">
                                <col width="67%">
                            </colgroup>"""
                    yield "<thead>"
                    yield "<tr class='w-100'>"
                    yield "<th colspan='2' class='bg-brand-light-color brand-dark-color tl'>"
                    yield self.render_graph_resource(c)
                    yield "</th></tr></thead>"

                yield self.render_po_tr(uri, c, level=0)

                if header:
                    yield "</table>"

        return "\n".join(contents())

    def render(self, graph: Graph, *, base="") -> str:
        self.g = graph
        return self.title(self.uri, base=base) + self.po_table(self.uri) + "</div>"


def subjectsForBaseQuery(base: str):
    return f"""
    SELECT DISTINCT ?s 
    WHERE {{
        ?s ?p ?o .
        optional {{ ?s a ?type . }}
        filter strStarts( str(?s), '{base}' )
        bind ( replace( str(?s), '{base}', '' ) as ?lname )
        bind (
                if(
                    regex(str(?lname), "^[a-z]")  # starts with [a-z]
                    ,concat(?lname, ' ')  # then append to sort after
                    ,str(?lname) # else return as-is
                )
            as ?sortName )
    }}
    order by
        lcase(?sortName)
    """


def main():

    dataset = Dataset(default_union=True)

    for input_file in [Path(f) for f in CONFIG["staticld_ghpages"]["input_files"]]:
        g = dataset.graph(URIRef(input_file.absolute().as_uri()))
        g.parse(str(input_file), format=input_file.suffix[1:])

    dataset.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

    onto = []
    vocab = []

    onto_base = CONFIG["staticld_ghpages"]["onto_base"]
    vocab_base = CONFIG["staticld_ghpages"]["vocab_base"]

    with open("./_includes/def.html", "w+") as onto_file:
        for s in dataset.query(subjectsForBaseQuery(onto_base)):
            concept = OntologyConcept(s.get("s"))
            display = concept.render(dataset, base=onto_base)
            onto_file.write(display)

    with open("./_includes/vocab.html", "w+") as vocab_file:
        for s in dataset.query(subjectsForBaseQuery(vocab_base)):
            concept = OntologyConcept(s.get("s"))
            display = concept.render(dataset, base=vocab_base)

            vocab_file.write(display)


if __name__ == "__main__":
    main()
