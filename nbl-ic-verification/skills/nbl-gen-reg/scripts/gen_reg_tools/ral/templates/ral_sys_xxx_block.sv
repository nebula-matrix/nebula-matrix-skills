{% set top = tpl_dict["top_name"] %}
{% set subpart = tpl_dict["subpart"] %}
class ral_sys_{{top}} extends project_reg_block;

    {%for bt in subpart%}
    {% if bt["inst_num"] == 1 %}
    rand ral_block_{{bt["name"]}} {{bt["name"]}};
    {% else %}
    rand ral_block_{{bt["name"]}} {{bt["name"]}}[{{bt["inst_num"]}}];
    {% endif %}
    {% endfor %}

	function new(string name = "{{top}}");
		super.new(name);
	endfunction: new

	function void build();
        this.default_map = create_map("", 0, 4, UVM_LITTLE_ENDIAN, 1);
        {%for bt in subpart%}
        {% if bt["inst_num"] == 1 %}
        this.{{bt["name"]}} = ral_block_{{bt["name"]}}::type_id::create("{{bt["name"]}}",,get_full_name());
        this.{{bt["name"]}}.configure(this, "`{{bt["name"] | upper}}_REG_TOP_PATH");
        this.{{bt["name"]}}.build();
        {%if subpart|length > 1%}
        this.default_map.add_submap(this.{{bt["name"]}}.default_map, `UVM_REG_ADDR_WIDTH'h{{bt["baseaddr_hex"]}});
        {%else%}
        this.default_map.add_submap(this.{{bt["name"]}}.default_map, `UVM_REG_ADDR_WIDTH'h0);
        {% endif %}
        {% else %}
        foreach (this.{{bt["name"]}}[i]) begin
            int J = i;
            this.{{bt["name"]}}[J] = ral_block_{{bt["name"]}}::type_id::create($psprintf("{{bt["name"]}}[%0d]", J),,get_full_name());
            this.{{bt["name"]}}[J].configure(this, $psprintf("`{{bt["name"] | upper}}_REG_TOP_PATH_%0d", J));
            this.{{bt["name"]}}[J].build();
            this.default_map.add_submap(this.{{bt["name"]}}[J].default_map, `UVM_REG_ADDR_WIDTH'h{{bt["baseaddr_hex"]}}+J*`UVM_REG_ADDR_WIDTH'h{{bt["size_hex"]}});
        end
        {% endif %}
        {% endfor %}
        `ifdef BACKDOOR
        {%for bt in subpart%}
        {% set regpart = bt["subpart"] %}
        `ifndef NOBACKDOOR_{{bt["name"] | upper}}
        {%for reg in regpart%}
        {% if reg["type"] != "tbl" and reg["type"] != "table"%}
        {% if reg["depth"] != 1 %}
            foreach (this.{{bt["name"]}}.{{reg["name"]}}[i0]) begin
			    {#ral_reg_{{top}}_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}.{{reg["name"]}}[i0].get_full_name(), i0);#}
			    ral_reg_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}.{{reg["name"]}}[i0].get_full_name(), i0);
			    this.{{bt["name"]}}.{{reg["name"]}}[i0].set_backdoor(bkdr);
		    end
        {% elif bt["inst_num"] != 1%}
            foreach (this.{{bt["name"]}}[i0]) begin
			    {#ral_reg_{{top}}_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}[i0].{{reg["name"]}}.get_full_name(), i0);#}
			    ral_reg_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}[i0].{{reg["name"]}}.get_full_name(), i0);
			    this.{{bt["name"]}}[i0].{{reg["name"]}}.set_backdoor(bkdr);
		    end
        {% else %}
            begin
                {#ral_reg_{{top}}_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}.{{reg["name"]}}.get_full_name());#}
                ral_reg_{{bt["name"]}}_{{reg["name"]}}_bkdr bkdr = new(this.{{bt["name"]}}.{{reg["name"]}}.get_full_name());
			    this.{{bt["name"]}}.{{reg["name"]}}.set_backdoor(bkdr);
            end
        {% endif %}
        {% endif %}
        {% endfor %}
        `endif
        {% endfor %}
        `endif //BACKDOOR
	    uvm_config_db #(project_reg_block)::set(null,"","RegisterModel_Debug",this);
	endfunction : build

	`uvm_object_utils(ral_sys_{{top}})
endclass : ral_sys_{{top}}

`endif

