{% set top = tpl_dict["top_name"] %}
{% set TOP = tpl_dict["top_name"] | upper() %}
`ifdef BACKDOOR

    `ifndef RAL_{{ TOP }}_BLOCK_INTF
    `define RAL_{{ TOP }}_BLOCK_INTF

    `ifndef GATE_SIM
    //////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////Front Sim//////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////
	interface ral_{{ top }}_block_intf;
		import uvm_pkg::*;
        `ifdef VCS
		initial uvm_resource_db#(virtual ral_{{ top }}_block_intf)::set("*", "uvm_reg_bkdr_if", interface::self());
        `endif

{% for bt_dict in tpl_dict["subpart"] %}
    {% set bn = bt_dict["name"] %}
    {% set BN = bt_dict["name"] | upper() %}
    {% set inst_num   = bt_dict["inst_num"] %}
    {% set max_dw_a32 = bt_dict["max_dw_a32"] %}

        `ifndef NOBACKDOOR_{{ BN }}

    {% if inst_num == 1 %}
        {% for reg_item in bt_dict["subpart"] %}
            {% if reg_item["depth"]==1 %}
                {% if reg_item["type"] == "reg" %} {#########################  1 inst, 1 depth, norm_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw);
            begin
                rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                {% set lsb = field_item["lsb"] %}
                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                    {% else %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data;
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw);
            begin
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                {% set lsb = field_item["lsb"] %}
                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% else %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

                {% elif reg_item["type"] == "wide_reg" %} {#########################  1 inst, 1 depth, wide_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw);
            begin
                rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                    {% set lsb = field_item["lsb"] %}
                    {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% set widx= 0 +field_item["widx"] %}

                    {% if field_item["rw_attr"] in ["ro"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                    {% elif field_item["rw_attr"] in ["rw"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                    {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw);
            begin
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                    {% set lsb = field_item["lsb"] %}
                    {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% set widx= 0 +field_item["widx"] %}

                    {% if field_item["rw_attr"] in ["ro"] %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% elif field_item["rw_attr"] in ["rw"] %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

                {% endif %} {#########################  1 inst, 1 depth end  #########################}
            {% else %}
                {% if reg_item["type"] == "reg" %} {#########################  1 inst, multi depth, norm_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% else %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                end
                    {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% else %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                end
                    {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"] == "wide_reg" %} {#########################  1 inst, multi depth, wide_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= depth+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= depth+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% endif %} {#########################  1 inst, multi depth end  #########################}
            {% endif %}
        {% endfor %}
    {% else %}
        {% for reg_item in bt_dict["subpart"] %}
            {% if reg_item["depth"]==1 %}
                {% if reg_item["type"]=="reg" %} {#########################  multi inst, 1 depth norm_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                        {% set lsb = field_item["lsb"] %}
                        {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% else %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                        {% set lsb = field_item["lsb"] %}
                        {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% else %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"]=="wide_reg" %} {#########################  multi inst, 1 depth wide_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= 0+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= 0+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% endif %}
            {% else %}
                {% if reg_item["type"]=="reg" %} {#########################  multi inst, multi depth norm_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case( depth_idx )
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% else %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case( depth_idx )
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% else %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"]=="wide_reg" %} {#########################  multi inst, multi depth wide_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                                {% set lsb = field_item["lsb"] %}
                                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% set widx= depth+field_item["widx"] %}
                                {% if field_item["rw_attr"] in ["ro"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                                {% elif field_item["rw_attr"] in ["rw"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                                {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                                {% set lsb = field_item["lsb"] %}
                                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% set widx= depth+field_item["widx"] %}
                                {% if field_item["rw_attr"] in ["ro"] %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% elif field_item["rw_attr"] in ["rw"] %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask
                {% endif %}
            {% endif %}
        {% endfor %}
    {% endif %}
        `endif //NOBACKDOOR_{{ BN }}
{%endfor%}
	endinterface

    `else

    //////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////Gate Sim//////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////
	interface ral_{{ top }}_block_intf;
		import uvm_pkg::*;
        `ifdef VCS
		initial uvm_resource_db#(virtual ral_{{ top }}_block_intf)::set("*", "uvm_reg_bkdr_if", interface::self());
        `endif

{% for bt_dict in tpl_dict["subpart"] %}
    {% set bn = bt_dict["name"] %}
    {% set BN = bt_dict["name"] | upper() %}
    {% set inst_num = bt_dict["inst_num"] %}
    {% set max_dw_a32 = bt_dict["max_dw_a32"] %}

        `ifndef NOBACKDOOR_{{ BN }}

    {% if inst_num == 1 %}
        {% for reg_item in bt_dict["subpart"] %}
            {% if reg_item["depth"]==1 %}
                {% if reg_item["type"] == "reg" %} {#########################  1 inst, 1 depth, norm_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw);
            begin
                rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                {% set lsb = field_item["lsb"] %}
                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                    {% else %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data;
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw);
            begin
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                {% set lsb = field_item["lsb"] %}
                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                    {% else %}
                $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

                {% elif reg_item["type"] == "wide_reg" %} {#########################  1 inst, 1 depth, wide_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw);
            begin
                rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                    {% set lsb = field_item["lsb"] %}
                    {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% set widx= 0+field_item["widx"] %}
                    {% if field_item["rw_attr"] in ["ro"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                    {% elif field_item["rw_attr"] in ["rw"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                    {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw);
            begin
            {% for field_item in reg_item["subpart"] %}
                {% if field_item["name"] != "rsv" %}
                    {% set lsb = field_item["lsb"] %}
                    {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                    {% set widx= 0+field_item["widx"] %}
                    {% if field_item["rw_attr"] in ["ro"] %}
                `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}];
                    {% elif field_item["rw_attr"] in ["rw"] %}
                $disposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                    {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                    {% endif %}
                {% endif %}
            {% endfor %}
            end
        endtask

                {% endif %} {#########################  1 inst, 1 depth end  #########################}
            {% else %}
                {% if reg_item["type"] == "reg" %} {#########################  1 inst, multi depth, norm_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% else %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                end
                    {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% else %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                end
                    {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"] == "wide_reg" %} {#########################  1 inst, multi depth, wide_reg  #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= depth+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int depth_idx);
            case(depth_idx)
                {% for depth in range(reg_item["depth"]) %}
                {{depth}}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= depth+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] ;
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% endif %} {#########################  1 inst, multi depth end  #########################}
            {% endif %}
        {% endfor %}
    {% else %}
        {% for reg_item in bt_dict["subpart"] %}
            {% if reg_item["depth"]==1 %}
                {% if reg_item["type"]=="reg" %} {#########################  multi inst, 1 depth norm_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                        {% set lsb = field_item["lsb"] %}
                        {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% else %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                        {% set lsb = field_item["lsb"] %}
                        {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                    $deposit(`{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% else %}
                    $deposit(`{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"]=="wide_reg" %} {#########################  multi inst, 1 depth wide_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= 0+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: begin
                    rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                    {% for field_item in reg_item["subpart"] %}
                        {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                            {% set widx= 0+field_item["widx"] %}
                            {% if field_item["rw_attr"] in ["ro"] %}
                    `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] ;
                            {% elif field_item["rw_attr"] in ["rw"] %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                    $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                end
                {% endfor %}
            endcase
        endtask

                {% endif %}
            {% else %}
                {% if reg_item["type"]=="reg" %} {#########################  multi inst, multi depth norm_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case( depth_idx )
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% else %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case( depth_idx )
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                            {% set lsb = field_item["lsb"] %}
                            {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% if field_item["rw_attr"] in ["sctr", "rctr"] %}
                        $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% else %}
                        $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH_{{ inst }}.U_{{ reg_item["name"] | upper() }}_{{ field_item["name"] | upper() }}_{{depth}}.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

                {% elif reg_item["type"]=="wide_reg" %} {#########################  multi inst, multi depth wide_reg #########################}
        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_read(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                                {% set lsb = field_item["lsb"] %}
                                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% set widx= depth+field_item["widx"] %}
                                {% if field_item["rw_attr"] in ["ro"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ];
                                {% elif field_item["rw_attr"] in ["rw"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data;
                                {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                        rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] = `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt;
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

        task ral_{{ bn }}_{{ reg_item["name"] }}_bkdr_write(uvm_reg_item rw, int inst_idx, int depth_idx);
            case(inst_idx)
                {% for inst in range(inst_num) %}
                {{ inst }}: case(depth_idx)
                    {% for depth in range(reg_item["depth"]) %}
                    {{ depth }}: begin
                        rw.value[0] = `UVM_REG_DATA_WIDTH'h0;
                        {% for field_item in reg_item["subpart"] %}
                            {% if field_item["name"] != "rsv" %}
                                {% set lsb = field_item["lsb"] %}
                                {% set msb = field_item["lsb"]+field_item["bits"]-1 %}
                                {% set widx= depth+field_item["widx"] %}
                                {% if field_item["rw_attr"] in ["ro"] %}
                        `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.wreg_rdata[ {{ widx }}*{{ max_dw_a32 }} +: {{ max_dw_a32 }} ] = rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] ;
                                {% elif field_item["rw_attr"] in ["rw"] %}
                        $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_WREG_INST[{{ widx }}].U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_data, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% elif field_item["rw_attr"] in ["sctr", "rctr"] %}
                        $deposit( `{{ TOP }}_BLOCK_TOP_PATH.`{{ BN }}_REG_TOP_PATH.U_NBL_CTWREG_TOP.GEN_{{ field_item["rw_attr"] | upper() }}_INST.GEN_{{ field_item["rw_attr"] | upper() }}_REG_INST[{{ widx }}].U_NBL_SSHOT_{{ field_item["rw_attr"] | upper() }}_REG.U_NBL_{{ field_item["rw_attr"] | upper() }}_REG.o_cnt, rw.value[0][{{msb | ralign(2)}}:{{lsb | ralign(2)}}] );
                                {% endif %}
                            {% endif %}
                        {% endfor %}
                    end
                    {% endfor %}
                endcase
                {% endfor %}
            endcase
        endtask

                {% endif %}
            {% endif %}
        {% endfor %}
    {% endif %}
        `endif //NOBACKDOOR_{{ BN }}
{%endfor%}
	endinterface

    `endif //GATE_SIM
    `endif //RAL_{{ TOP }}_BLOCK_INTF
`endif //BACKDOOR
