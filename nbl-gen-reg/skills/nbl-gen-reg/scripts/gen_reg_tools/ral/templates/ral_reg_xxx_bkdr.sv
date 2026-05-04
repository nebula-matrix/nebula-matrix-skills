{% set top = tpl_dict["top_name"] %}
`ifndef PROJECT_REG_PKG__DEF
   `define PROJECT_REG_PKG__DEF
   import base_reg_pkg::*;
`endif

`ifndef RAL_SYS_{{top | upper}}
`define RAL_SYS_{{top | upper}}

`ifdef BACKDOOR
{% for bt_item in tpl_dict["subpart"] %}
{% set bn         = bt_item["name"] %}
{% set BN         = bt_item["name"] | upper() %}
`ifndef NOBACKDOOR_{{ BN }}
    {% for reg_item in bt_item["subpart"] %}
        {% set name  = reg_item["name"] %}
        {% set depth = reg_item["depth"] %}
        {% set typ   = reg_item["type"] %}
        {% if typ in ["reg", "wide_reg"] %}
            {% if depth == 1 and bt_item["inst_num"] == 1 %}
class ral_reg_{{ bn }}_{{ name }}_bkdr extends uvm_reg_backdoor;
    virtual ral_{{ top }}_block_intf __reg_vif;
	function new(string name);
		super.new(name);
		uvm_resource_db#(virtual ral_{{ top }}_block_intf)::read_by_name(get_full_name(), "uvm_reg_bkdr_if", __reg_vif);
	endfunction

	virtual task read(uvm_reg_item rw);
		do_pre_read(rw);
		__reg_vif.ral_{{ bn }}_{{ name }}_bkdr_read(rw);
		rw.status = UVM_IS_OK;
		do_post_read(rw);
	endtask

	virtual task write(uvm_reg_item rw);
		do_pre_write(rw);
		__reg_vif.ral_{{ bn }}_{{ name }}_bkdr_write(rw);
		rw.status = UVM_IS_OK;
		do_post_write(rw);
	endtask
endclass

            {% else %}
class ral_reg_{{ bn }}_{{ name }}_bkdr extends uvm_reg_backdoor;
    virtual ral_{{ top }}_block_intf __reg_vif;
    int                             depth_idx;
	function new(string name, int depth_idx);
		super.new(name);
		uvm_resource_db#(virtual ral_{{ top }}_block_intf)::read_by_name(get_full_name(), "uvm_reg_bkdr_if", __reg_vif);
        this.depth_idx = depth_idx;
	endfunction

	virtual task read(uvm_reg_item rw);
		do_pre_read(rw);
		__reg_vif.ral_{{ bn }}_{{ name }}_bkdr_read(rw, this.depth_idx);
		rw.status = UVM_IS_OK;
		do_post_read(rw);
	endtask

	virtual task write(uvm_reg_item rw);
		do_pre_write(rw);
		__reg_vif.ral_{{ bn }}_{{ name }}_bkdr_write(rw, this.depth_idx);
		rw.status = UVM_IS_OK;
		do_post_write(rw);
	endtask
endclass

            {% endif %}
        {% endif %}
    {% endfor %}
`endif  //NOBACKDOOR_{{ BN }}
{% endfor %}
`endif  //BACKDOOR
