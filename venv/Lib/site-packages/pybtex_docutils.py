"""
API
~~~

The backend renders :class:`pybtex.richtext.Text` instances
into a list of :class:`docutils.nodes.Text`
and :class:`docutils.nodes.inline` instances (or subclasses of these).
For typical use cases, all you need to care about are the methods
:meth:`Backend.paragraph`,
:meth:`Backend.citation`, and
:meth:`Backend.citation_reference`
which are to be called on *formatted* entries,
as in the :ref:`minimal example <minimal-example>`.

Note that you should not import the :mod:`pybtex_docutils` module directly.
Instead, use pybtex's plugin system to get the :class:`Backend` class,
again,
as in the :ref:`minimal example <minimal-example>`.

.. autoclass:: Backend
   :show-inheritance:
   :members: RenderType, paragraph, citation, citation_reference
"""

import docutils.nodes
import itertools

from pybtex.backends import BaseBackend
import pybtex.richtext
import six


class Backend(BaseBackend):
    name = 'docutils'

    symbols = {
        'ndash': [docutils.nodes.Text(u'\u2013', u'\u2013')],
        'newblock': [docutils.nodes.Text(u' ', u' ')],
        'nbsp': [docutils.nodes.Text(u'\u00a0', u'\u00a0')],
    }
    tags = {
        'emph': docutils.nodes.emphasis,  # note: deprecated
        'em': docutils.nodes.emphasis,
        'strong': docutils.nodes.strong,
        'i': docutils.nodes.emphasis,
        'b': docutils.nodes.strong,
        'tt': docutils.nodes.literal,
    }
    RenderType = list

    # for compatibility only
    def format_text(self, text):
        return self.format_str(text)

    def format_str(self, str_):
        assert isinstance(str_, six.string_types)
        return [docutils.nodes.Text(str_, str_)]

    def format_tag(self, tag_name, text):
        assert isinstance(tag_name, six.string_types)
        assert isinstance(text, self.RenderType)
        if tag_name in self.tags:
            tag = self.tags[tag_name]
            return [tag('', '', *text)]
        else:
            return text

    def format_href(self, url, text):
        assert isinstance(url, six.string_types)
        assert isinstance(text, self.RenderType)
        node = docutils.nodes.reference('', '', *text, refuri=url)
        return [node]

    def write_entry(self, key, label, text):
        raise NotImplementedError("use Backend.citation() instead")

    def render_sequence(self, rendered_list):
        return list(itertools.chain(*rendered_list))

    def paragraph(self, entry):
        """Return a docutils.nodes.paragraph
        containing the rendered text for *entry* (without label).

        .. versionadded:: 0.2.0
        """
        return docutils.nodes.paragraph('', '', *entry.text.render(self))

    def citation(self, entry, document, use_key_as_label=True):
        """Return citation node, with key as name, label as first
        child, and paragraph with entry text as second child. The citation is
        expected to be inserted into *document* prior to any docutils
        transforms.
        """
        # see docutils.parsers.rst.states.Body.citation()
        if use_key_as_label:
            label = entry.key
        else:
            label = entry.label
        name = docutils.nodes.fully_normalize_name(entry.key)
        text = entry.text.render(self)
        citation = docutils.nodes.citation()
        citation['names'].append(name)
        citation += docutils.nodes.label('', label)
        citation += self.paragraph(entry)
        document.note_citation(citation)
        document.note_explicit_target(citation, citation)
        return citation

    def citation_reference(self, entry, document, use_key_as_label=True):
        """Return citation_reference node to the given citation. The
        citation_reference is expected to be inserted into *document*
        prior to any docutils transforms.
        """
        # see docutils.parsers.rst.states.Body.footnote_reference()
        if use_key_as_label:
            label = entry.key
        else:
            label = entry.label
        refname = docutils.nodes.fully_normalize_name(entry.key)
        refnode = docutils.nodes.citation_reference(
            '[%s]_' % label, refname=refname)
        refnode += docutils.nodes.Text(label)
        document.note_citation_ref(refnode)
        return refnode

    def footnote(self, entry, document):
        """Return footnote node, with key as name, and paragraph with
        entry text as child. The footnote is expected to be
        inserted into *document* prior to any docutils transforms.
        """
        # see docutils.parsers.rst.states.Body.footnote()
        name = docutils.nodes.fully_normalize_name(entry.key)
        footnote = docutils.nodes.footnote(auto=1)
        footnote['names'].append(name)
        footnote += self.paragraph(entry)
        document.note_autofootnote(footnote)
        document.note_explicit_target(footnote, footnote)
        return footnote

    def footnote_reference(self, entry, document):
        """Return footnote_reference node to the given citation. The
        footnote_reference is expected to be inserted into *document*
        prior to any docutils transforms.
        """
        # see docutils.parsers.rst.states.Body.footnote_reference()
        refname = docutils.nodes.fully_normalize_name(entry.key)
        refnode = docutils.nodes.footnote_reference(
            '[#%s]_' % entry.key, refname=refname, auto=1)
        document.note_autofootnote_ref(refnode)
        document.note_footnote_ref(refnode)
        return refnode
