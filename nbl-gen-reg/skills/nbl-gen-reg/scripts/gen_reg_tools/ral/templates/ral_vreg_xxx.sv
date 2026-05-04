{% for tbl_dict in tpl_dict.get("subpart") %}
{% set bn    = tbl_dict.get("bn") %}
{% set tn    = tbl_dict.get("name") %}
{% set nbits = tbl_dict.get("nbits") %}
class ral_vreg_{{ bn }}_{{ tn }}_vreg extends uvm_vreg;
    {% for field_dict in tbl_dict.get("subpart") %}
        {% if field_dict["name"] != "rsv" %}
    rand uvm_vreg_field {{ field_dict["name"] }};
        {% endif %}
    {% endfor %}

    function new(string name = "ral_vreg_{{ bn }}_{{ tn }}_vreg", int unsigned n_bits = {{ nbits }});
        super.new(name, n_bits);
        {% for field_dict in tbl_dict.get("subpart") %}
            {% if field_dict["name"] != "rsv" %}
        this.{{ field_dict["name"] }} = uvm_vreg_field::type_id::create("{{ field_dict["name"] }}",,get_full_name());
        this.{{ field_dict["name"] }}.configure(this, {{ field_dict["bits"] }}, {{ field_dict["lsb"] }});
            {% endif %}
        {% endfor %}
    endfunction: new
 
    `uvm_object_utils(ral_vreg_{{ bn }}_{{ tn }}_vreg)

endclass : ral_vreg_{{ bn }}_{{ tn }}_vreg
{% endfor %}