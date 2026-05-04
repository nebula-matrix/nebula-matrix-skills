{% set mdl          =   tpl_dict["common"]["module_name"] %}
{% set max_dw_len   =   tpl_dict["common"]["max_dw_len"] %}
{% set max_name_len =   tpl_dict["common"]["max_name_len"] %}
module {{ mdl }}_reg_slv
(
    // input norem_reg
{% for item_dict in tpl_dict["iport"] %}
    {% if item_dict["dw"]==1 or item_dict["dw"] in [Null, None]  %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
    // input tbl
{% for item_dict in tpl_dict["tbl_iport"] %}
    {% if item_dict["dw"]==1 or item_dict["dw"] in [Null, None]  %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
    // input wreg
{% for item_dict in tpl_dict["wreg_iport"] %}
    {% if item_dict["dw"]==1 or item_dict["dw"] in [Null, None]  %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}}  {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
    // output norm_reg
{% for item_dict in tpl_dict["oport"] %}
    {% if item_dict["dw"]==1 or item_dict["dw"] in [Null, None]  %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
    // output tbl
{% for item_dict in tpl_dict["tbl_oport"] %}
    {% if item_dict["aw"]!=Null %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} [{{ item_dict["aw"] | ralign(max_dw_len+2) }}:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% elif item_dict["dw"]!=1 and item_dict["dw"]!=Null %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
    // output wreg
{% for item_dict in tpl_dict["wreg_oport"] %}
    {% if item_dict["dw"]==1 or item_dict["dw"]==Null  %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} {{ " " | lalign(max_dw_len + 6) }}         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% else %}
    {{item_dict["direct"]}} {{item_dict["unit"]}} [{{ item_dict["dw"] | ralign(max_dw_len) }}-1:0]         {{ item_dict["sig_name"] | lalign(max_name_len) }},
    {% endif %}
{% endfor %}
{% if tpl_dict["common"]["have_int"]==True %}
    // int
    output logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("o_reg_"+mdl+"_interupt") | lalign(max_name_len) }},
{% endif %}
{% if tpl_dict["common"]["have_wr_ctrl"]==True %}
    // wr_ctrl
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_wr_ctrl" | lalign(max_name_len) }},
{% endif %}
{% if tpl_dict["common"]["have_snap"]==True %}
    // snapshot
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_snapshot_trig" | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_sshot_mode_en" | lalign(max_name_len) }},
{% endif %} 
{% if tpl_dict["common"]["apb_intf_en"]==True %}
    // apb_intf
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_pclk"     | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_prst_n"   | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_psel"     | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_penable"  | lalign(max_name_len) }},
    input  logic [{{25  | ralign(max_dw_len)}}-1:0]         {{ "i_paddr"    | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_pwrite"   | lalign(max_name_len) }},
    input  logic [{{32  | ralign(max_dw_len)}}-1:0]         {{ "i_pwdata"   | lalign(max_name_len) }},
    output logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_prdy"     | lalign(max_name_len) }},
    output logic [{{32  | ralign(max_dw_len)}}-1:0]         {{ "i_prdata"   | lalign(max_name_len) }},
    output logic {{ " " | lalign(max_dw_len + 6) }}         {{ "i_pslverr"  | lalign(max_name_len) }},
{% else %}
    // cif
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_req")    | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("i_cif_"+mdl+"_rw")     | lalign(max_name_len) }},
    input  logic [{{25  | ralign(max_dw_len)}}-1:0]         {{ ("i_cif_"+mdl+"_addr")   | lalign(max_name_len) }},
    input  logic [{{32  | ralign(max_dw_len)}}-1:0]         {{ ("i_cif_"+mdl+"_wdata")   | lalign(max_name_len) }},
    output logic {{ " " | lalign(max_dw_len + 6) }}         {{ ("o_"+mdl+"_cif_ack")    | lalign(max_name_len) }},
    output logic [{{32  | ralign(max_dw_len)}}-1:0]         {{ ("o_"+mdl+"_cif_rdata")  | lalign(max_name_len) }},
{% endif %}
    // clk/rst_n
{% set clk=tpl_dict["common"]["clk"] %}
{% set rst=tpl_dict["common"]["rst"] %}
{% if tpl_dict["common"]["multick"]==True %}
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ (clk + "_" + tpl_dict["common"]["clk_ls"][0] )   | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ (clk + "_" + tpl_dict["common"]["clk_ls"][1] )   | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ (rst + "_" + tpl_dict["common"]["clk_ls"][0] )   | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ (rst + "_" + tpl_dict["common"]["clk_ls"][1] )   | lalign(max_name_len) }}
{% else %}
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ clk    | lalign(max_name_len) }},
    input  logic {{ " " | lalign(max_dw_len + 6) }}         {{ rst    | lalign(max_name_len) }}
{% endif %}
);