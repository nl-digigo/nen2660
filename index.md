---
layout: page
title: "NEN 2660"
permalink: /
---

## Rules for information modelling of the built environment

These pages provide a way to lookup and dereference the concepts of 
<a href='-/downloads#norm' class='link dim underline-hover blue'>
NEN 2660-2:2022</a>.

***

{% assign pp = site.pages | sort: "sortkey" %}
{% for p in pp %}

{% unless p.url == page.url %}
{% unless p.dont_render %}
{% if p.title %}
<h3 class='f5 db mb4'>
<a
  class="link"
  href="{{ site.baseurl }}{{p.url | remove: '.html'}}">
  <span class='db black mb2'>{{p.title}}</span>
  <span class='dim underline-hover brand-dark-color f3'>{{p.excerpt}}</span>
</a>
</h3>

{% endif %}
{% endunless %}
{% endunless %}

{% endfor %}

<h3 class='f5 db mb4'>
<a
  class="link"
  href="https://nen2660.ontology-viewer.com/">
  <span class='db black mb2'>Viewer</span>
  <span class='dim underline-hover brand-dark-color f3'>NEN2660-2 Ontology viewer</span>
</a>
</h3>

***

You may discuss implementation and usage on GitHub at 
<a href='{{ site.repo }}/discussions/' class='link'>
nl-digigo/nen2660</a>.
