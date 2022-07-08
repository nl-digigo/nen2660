---
layout: page
title: SPARQL-Endpoint
permalink: /-/query
excerpt: Query using SPARQL
sortkey: 2
enableYasgui: true
wider: true
---

## Query NEN 2660-2 using SPARQL

The NEN 2660-2 ontology is available as static, downloadable [files][downloads].
For dynamic integration, exploration and queries, [Stichting CROW][crow] provides a public SPARQL-endpoint at:

<center><b>https://w3id.org/nen2660/sparql</b></center>

[crow]: https://www.crow.nl
[yasgui]: https://triply.cc/docs/yasgui

[downloads]: {{ site.baseurl }}/-/downloads

---

<div id="yasgui"></div>
<script>
  const yasgui = new Yasgui(document.getElementById("yasgui"), {
    requestConfig: {
      endpoint: "https://w3id.org/nen2660/sparql",
      method: "GET"
    }
  });
  const tab = yasgui.getTab();
  tab.setQuery(`
SELECT
  ?subj ?pred ?obj
WHERE {
  ?subj ?pred ?obj .
}
LIMIT 25
`);
  const yasqe = yasgui.getTab().yasqe;
  yasqe.addPrefixes({
    "nen2660":"https://w3id.org/nen2660/def#",
    "nen2660-term":"https://w3id.org/nen2660/term#",
    "owl":"http://www.w3.org/2002/07/owl#",
    "quantitykind":"http://qudt.org/vocab/quantitykind/",
    "qudt":"http://qudt.org/schema/qudt/",
    "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
    "sh":"http://www.w3.org/ns/shacl#",
    "skos":"http://www.w3.org/2004/02/skos/core#",
    "time":"http://www.w3.org/2006/time#",
    "xsd":"http://www.w3.org/2001/XMLSchema#",
  });
  yasqe.collapsePrefixes(true);

</script>

---

The SPARQL-endpoint provided services `GET` or `POST` HTTP-requests according to the following (Source: [Laces Hub][laceshub]):

> - with a `GET` query request, the percent-encoded query is passed as the value of the "query" parameter,
> - with a `POST` query request the query is passed in the body of the request and the "Content-Type" header is set to "application/sparql-query".
>
> Among the format of the result can be set using the "Accept" header, the following formats are supported:
>
> - JSON = `application/json`
> - CSV = `text/csv`
> - XML = `application/sparql-results+xml`
> - TSV = `text/tab-separated-values`

[laceshub]: https://docs.laces.tech/hub/9.0.8/querying.html

---

This query interface is provided by [Triply’s Yasgui][yasgui].
