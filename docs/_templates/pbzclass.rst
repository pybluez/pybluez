
+------------------+------------------+---------------+
| :ref:`genindex`  | :ref:`modindex`  | :ref:`search` | 
+------------------+------------------+---------------+

.. _{{fullname}}:

{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

A class defined in module :ref:`{{module}}`.

.. autoclass:: {{ objname }}
  :show-inheritance:

   {% block methods %}

   .. automethod:: __init__
     :noindex:

   {% if methods %}
   .. rubric:: Methods

   .. autosummary::
     :toctree: methods
     :template: pbzmethod.rst

   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

+------------------+------------------+---------------+
| :ref:`genindex`  | :ref:`modindex`  | :ref:`search` | 
+------------------+------------------+---------------+
