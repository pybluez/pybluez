
+------------------+------------------+---------------+
| :ref:`genindex`  | :ref:`modindex`  | :ref:`search` | 
+------------------+------------------+---------------+

.. _{{fullname}}:

{{ objname | escape | underline}}

.. automodule:: {{ fullname }}
   :show-inheritance:

   {% block functions %}
   {% if functions %}
   .. rubric:: Functions

   .. autosummary::
     :nosignatures:
     :toctree: functions
     :template: pbzfunction.rst

   {% for item in functions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: Classes

   .. autosummary::
     :nosignatures:
     :toctree: classes
     :template: pbzclass.rst

   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: Exceptions

   .. autosummary::
     :toctree: exceptions
     :template: pbzexception.rst

   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

+------------------+------------------+---------------+
| :ref:`genindex`  | :ref:`modindex`  | :ref:`search` | 
+------------------+------------------+---------------+
