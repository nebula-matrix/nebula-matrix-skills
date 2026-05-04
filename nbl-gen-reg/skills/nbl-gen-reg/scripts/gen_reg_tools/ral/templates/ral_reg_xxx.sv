{% set subpart = tpl_dict["subpart"] %}
    {%for bt in subpart%}
    {% set regpart = bt["subpart"] %}
    {%for reg in regpart%}
    {% set fieldpart = reg["subpart"] %}
    {% if reg["type"]|lower == "tbl" or reg["type"]|lower == "table"%}
class ral_mem_{{bt["name"]}}_{{reg["name"]}} extends project_mem;
    function new(string name = "{{bt["name"]}}_{{reg["name"]}}");
        super.new(name, `UVM_REG_ADDR_WIDTH'h{{reg["depth"]}}, {{reg["width"]}}, "RW", build_coverage(UVM_NO_COVERAGE));
    endfunction
    virtual function void build();
        {% if reg["tbl_rw_attr"] == "rw" %}
        this.set_mask(`UVM_REG_DATA_WIDTH'h{{reg["tbl_data_width"]}}, `UVM_REG_DATA_WIDTH'h{{reg["tbl_data_width"]}});
        {%else%}
        this.set_mask(`UVM_REG_DATA_WIDTH'h{{reg["tbl_data_width"]}}, `UVM_REG_DATA_WIDTH'h0);
        {%endif%}
        this.set_reset(`UVM_REG_DATA_WIDTH'h0);
    endfunction: build

    `uvm_object_utils(ral_mem_{{bt["name"]}}_{{reg["name"]}})

endclass : ral_mem_{{bt["name"]}}_{{reg["name"]}}


class ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg extends uvm_vreg;
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
	rand uvm_vreg_field {{field["field"]}};
    {% endif %}
    {% endfor %}

    function new(string name = "ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg", int unsigned n_bits = {{reg["tbl_nbits"]}});
        super.new(name, n_bits);
        {%for field in fieldpart%}
        {% if field["field"] != "rsv" %}
        this.{{field["field"]}} = uvm_vreg_field::type_id::create("{{field["field"]}}",,get_full_name());
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}});
        {% endif %}
        {% endfor %}
    endfunction: new

    `uvm_object_utils(ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg)

endclass : ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg


    {% else %}{##############not tbl##################}
class ral_reg_{{bt["name"]}}_{{reg["name"]}} extends project_reg;
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
	rand project_reg_field {{field["field"]}};
    {% endif %}
    {% endfor %}

    covergroup cg_vals ();
        option.per_instance = 1;
        {%for field in fieldpart%}
        {% if field["field"] != "rsv" %}
        {% if field["mbin"]|length+field["brace_new"]|length+field["rsv"]|length > 0 %}
        {{field["field"]}}_value : coverpoint {{field["field"]}}.value {
            {% if field["mbin"]|length > 0 %}
            {% for f in field["mbin"] %}
            {% if field["mbin_num"][loop.index0] > 1 %}
            bins bin_{{loop.index0}}[{{field["mbin_num"][loop.index0]}}] = {[{{f[0].replace("0x","'h")}}:{{f[1].replace("0x","'h")}}]};
            {% else %}
            bins bin_{{loop.index0}} = {[{{f[0].replace("0x","'h")}}:{{f[1].replace("0x","'h")}}]};
            {% endif %}
            {% endfor %}
            {% endif %}
            {% if field["brace_new"]|length > 0 %}
            {% for f in field["brace_new"] %}
            bins bin_brace_{{loop.index0}} = {{'{'}}{{f}}};
            {% endfor %}
            {% endif %}
            {% if field["rsv"]|length > 0 %}
            bins bin_rsv = {
            {%- for f in field["rsv"] -%}
            {%- if loop.index < field["rsv"]|length -%}
            [{{f[0].replace("0x","'h")}}:{{f[1].replace("0x","'h")}}],
            {%- else -%}
            [{{f[0].replace("0x","'h")}}:{{f[1].replace("0x","'h")}}]
            {%- endif -%}
            {%- endfor -%}
            };
            {% endif %}
            option.weight = {{field["weight"]}};
        }
        {% endif %}
        {% endif %}
        {% endfor %}
    endgroup : cg_vals

	function new(string name = "{{bt["name"]}}_{{reg["name"]}}");
		super.new(name, {{reg["width"]}},build_coverage(UVM_CVR_FIELD_VALS));
		add_coverage(build_coverage(UVM_CVR_FIELD_VALS));
		if (has_coverage(UVM_CVR_FIELD_VALS))
			cg_vals = new();
	endfunction: new
    virtual function void build();
        {%for field in fieldpart%}
        {% if field["field"] != "rsv" %}
        this.{{field["field"]}} = project_reg_field::type_id::create("{{field["field"]}}",,get_full_name());
        {%if field["rw_attr"] == "rwc"%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "W1C", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        {%elif field["rw_attr"] == "rww"%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "RW", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        {%elif field["rw_attr"] == "sctr" or field["rw_attr"] == "rctr"%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "WRC", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        this.{{field["field"]}}.set_rc_type("{{field["rw_attr"] | upper}}");
        {%elif field["rw_attr"] == "min" or field["rw_attr"] == "max"%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "WRS", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        this.{{field["field"]}}.set_rc_type("{{field["rw_attr"] | upper}}");
        {%elif field["rw_attr"] == "rc"%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "{{field["rw_attr"] | upper}}", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        this.{{field["field"]}}.set_rc_type("{{field["rw_attr"] | upper}}");
        {%else%}
        this.{{field["field"]}}.configure(this, {{field["bits"]}}, {{field["lsb"]}}, "{{field["rw_attr"] | upper}}", 0, {{field["bits"]}}'h{{field["default_value_hex"]}}, 1, 0, 1);
        {% endif %}
        {% endif %}
        {% endfor %}
    endfunction: build

	`uvm_object_utils(ral_reg_{{bt["name"]}}_{{reg["name"]}})


	function void sample_values();
	   super.sample_values();
	   if (get_coverage(UVM_CVR_FIELD_VALS)) begin
	      if(cg_vals!=null) cg_vals.sample();
	   end
	endfunction
endclass : ral_reg_{{bt["name"]}}_{{reg["name"]}}


    {% endif %}
    {% endfor %}
    {% endfor %}


