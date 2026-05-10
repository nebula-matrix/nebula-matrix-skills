{% set subpart = tpl_dict["subpart"] %}
    {%for bt in subpart%}
    `ifdef {{bt["name"] | upper}}_MEM_BACKDOOR_ENABLE
        `include "ral_{{bt["name"]}}_backdoor.sv"
    `endif
class ral_block_{{bt["name"]}} extends project_reg_block;
    {% set regpart = bt["subpart"] %}
    {%for reg in regpart%}
    {% if reg["type"] == "tbl" or reg["type"] == "table"%}
    rand ral_mem_{{bt["name"]}}_{{reg["name"]}} {{reg["name"]}};
    rand ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg {{reg["name"]}}_vreg;
    {% elif reg["depth"] != 1 %}
    rand ral_reg_{{bt["name"]}}_{{reg["name"]}} {{reg["name"]}}[{{reg["depth"]}}];
    {% else %}
    rand ral_reg_{{bt["name"]}}_{{reg["name"]}} {{reg["name"]}};
    {% endif %}
    {% endfor %}
    {%for reg in regpart%}
    {% set fieldpart = reg["subpart"] %}
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
    {% if reg["type"] == "tbl" or reg["type"] == "table"%}
    rand uvm_vreg_field {{reg["name"]}}_vreg_{{field["field"]}};
    {% elif reg["depth"] != 1 %}
    rand project_reg_field {{reg["name"]}}_{{field["field"]}}[{{reg["depth"]}}];
    {% else %}
    rand project_reg_field {{reg["name"]}}_{{field["field"]}};
    {% endif %}
    {% endif %}
    {% endfor %}
    {% endfor %}

    function new(string name = "{{bt["name"]}}");
		super.new(name, build_coverage(UVM_CVR_FIELD_VALS));
		add_coverage(build_coverage(UVM_CVR_FIELD_VALS));
	endfunction: new

    virtual function void build();
        this.default_map = create_map("", 0, 4, UVM_LITTLE_ENDIAN, 1);
    {%for reg in regpart%}
    {% set fieldpart = reg["subpart"] %}
    {% if reg["type"] == "tbl" or reg["type"] == "table"%}
        this.{{reg["name"]}} = ral_mem_{{bt["name"]}}_{{reg["name"]}}::type_id::create("{{reg["name"]}}",,get_full_name());
        this.{{reg["name"]}}.configure(this, "");
        this.{{reg["name"]}}.build();
        this.default_map.add_mem(this.{{reg["name"]}}, `UVM_REG_ADDR_WIDTH'h{{reg["offset_addr"]}}, "RW", 0);
        this.{{reg["name"]}}_vreg = ral_vreg_{{bt["name"]}}_{{reg["name"]}}_vreg::type_id::create("{{reg["name"]}}_vreg",,get_full_name());
        this.{{reg["name"]}}_vreg.configure(this, {{reg["name"]}}, 64'd{{reg["depth_dec"]}}, 'h0, 0);
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
		this.{{reg["name"]}}_vreg_{{field["field"]}} = this.{{reg["name"]}}_vreg.{{field["field"]}};
    {% endif %}
    {% endfor %}
    {% elif reg["depth"] != 1 %}{###########for not tbl############}
        foreach(this.{{reg["name"]}}[i])begin
            int J = i;
            this.{{reg["name"]}}[J] = ral_reg_{{bt["name"]}}_{{reg["name"]}}::type_id::create($psprintf("{{reg["name"]}}[%0d]",J),,get_full_name());
            this.{{reg["name"]}}[J].configure(this, null, "");
            this.{{reg["name"]}}[J].build();
            this.{{reg["name"]}}[J].add_hdl_path('{
        {%for field in fieldpart%}
        {% if field["field"] != "rsv" %}
        {% if loop.index < reg["field_len_rm_rsv_lsb"] %}
                '{$psprintf("U_{{reg["name"] | upper}}%0d.{{field["field"] | upper}}__.o_data",J), {{field["lsb"]}}, {{field["bits"]}}},
        {% else %}
                '{$psprintf("U_{{reg["name"] | upper}}%0d.{{field["field"] | upper}}__.o_data",J), {{field["lsb"]}}, {{field["bits"]}}}
        {% endif %}
        {% endif %}
        {% endfor %}
             });
            this.default_map.add_reg(this.{{reg["name"]}}[J], `UVM_REG_ADDR_WIDTH'h{{reg["offset_addr"]}}+J*`UVM_REG_ADDR_WIDTH'h{{reg["byte_width"]}}, "RW", 0);
            {% if reg["snapshot_en"]=="y" %}
            this.{{reg["name"]}}[J].set_snaps_en(1);
            {% endif %}
        {%for field in fieldpart%}
        {% if field["field"] != "rsv" %}
	    	this.{{reg["name"]}}_{{field["field"]}}[J] = this.{{reg["name"]}}[J].{{field["field"]}};
        {% endif %}
        {% endfor %}
        end
    {% else %}{###########for not tbl and depth==1 ############}
        this.{{reg["name"]}} = ral_reg_{{bt["name"]}}_{{reg["name"]}}::type_id::create("{{reg["name"]}}",,get_full_name());
        this.{{reg["name"]}}.configure(this, null, "");
        this.{{reg["name"]}}.build();
        this.{{reg["name"]}}.add_hdl_path('{
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
    {% if loop.index < reg["field_len_rm_rsv_lsb"] %}
            '{"U_{{reg["name"] | upper}}.{{field["field"] | upper}}__.o_data", {{field["lsb"]}}, {{field["bits"]}}},
    {% else %}
            '{"U_{{reg["name"] | upper}}.{{field["field"] | upper}}__.o_data", {{field["lsb"]}}, {{field["bits"]}}}
    {% endif %}
    {% endif %}
    {% endfor %}
         });
        {%if loop.index == 1%}{#TODO must debug#}
        this.default_map.add_reg(this.{{reg["name"]}}, `UVM_REG_ADDR_WIDTH'h0, "RW", 0);
        {%else%}
        this.default_map.add_reg(this.{{reg["name"]}}, `UVM_REG_ADDR_WIDTH'h{{reg["offset_addr"]}}, "RW", 0);
        {% endif %}
        {% if reg["snapshot_en"]=="y" %}
        this.{{reg["name"]}}.set_snaps_en(1);
        {% endif %}
    {%for field in fieldpart%}
    {% if field["field"] != "rsv" %}
		this.{{reg["name"]}}_{{field["field"]}} = this.{{reg["name"]}}.{{field["field"]}};
    {% endif %}
    {% endfor %}
    {% endif %}
    {% endfor %}{####################%for reg in regpart%##################}

        `ifdef {{bt["name"] | upper}}_MEM_BACKDOOR_ENABLE
            `include "ral_{{bt["name"]}}_set_backdoor.sv"
        `endif
   endfunction : build

	`uvm_object_utils(ral_block_{{bt["name"]}})

    function void sample_values();
	   super.sample_values();
		if (get_coverage(UVM_CVR_FIELD_VALS)) begin
            {%for reg in regpart%}
            {% if reg["type"] != "tbl" and reg["type"] != "table"%}
            {% if reg["depth"] != 1 %}
            foreach({{reg["name"]}}[i])begin
			    if ({{reg["name"]}}[i].cg_vals != null) {{reg["name"]}}[i].cg_vals.sample();
            end
            {%else%}
			if ({{reg["name"]}}.cg_vals != null) {{reg["name"]}}.cg_vals.sample();
            {%endif%}
            {%endif%}
            {% endfor %}
        end
	endfunction
endclass : ral_block_{{bt["name"]}}
    {% endfor %}{############%for bt in subpart%##################}

