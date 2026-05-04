{% set ckp          = tpl_dict["ck_domain"]                 %}
{% set clk          = tpl_dict["common"]["clk"]             %}
{% set rst          = tpl_dict["common"]["rst"]             %}
{% if tpl_dict["common"]["low_rst"]==True %}
    {% if tpl_dict["common"]["sync_rst"]==True %}
        {% set alw_clk      = "always_ff @(posedge %s) begin"%(clk+ckp) %}
        {% set alw_rst_jud  = "if(~%s)begin"%(rst+ckp) %}
    {% else %}
        {% set alw_clk      = "always_ff @(posedge %s or negedge %s) begin"%(clk+ckp, rst+ckp) %}
        {% set alw_rst_jud  = "if(~%s)begin"%(rst+ckp) %}
    {% endif %}
{% else %}
    {% if tpl_dict["common"]["sync_rst"]==True %}
        {% set alw_clk      = "always_ff @(posedge %s) begin"%(clk+ckp) %}
        {% set alw_rst_jud  = "if(%s)begin"%(rst+ckp) %}
    {% else %}
        {% set alw_clk      = "always_ff @(posedge %s or posedge %s) begin"%(clk+ckp, rst+ckp) %}
        {% set alw_rst_jud  = "if(%s)begin"%(rst+ckp) %}
    {% endif %}
{% endif %}
//========================================================
// read process
//========================================================
{% for item_dict in tpl_dict["rd_blk_ls"] %}
{% set idx = item_dict["grp_id"] %}
{% set aw  = tpl_dict["common"]["reg_dw"] %}
{% set align_len = item_dict["align_max_len"] %}
{{alw_clk}}
    {{alw_rst_jud}}
        norm_reg_hit{{ ckp }}[{{ idx }}] <= 1'h0;
        reg_rdata{{ ckp }}[{{ idx }}]    <= {{ aw }}'h0;
    end
    else if ( reg_ren{{ ckp }}[{{ idx }}] ) begin
        case ( {reg_addr{{ ckp }}[{{ idx }}][24:2], 2'b0} )
    {% for case_opt in item_dict["case_opt_ls"] %}
            {{ case_opt | lalign(align_len) }} end
    {% endfor %}
            {{ item_dict["default"] | lalign(align_len) }} end
        endcase
    end
    else begin
        norm_reg_hit{{ ckp }}[{{ idx }}] <= 1'h0;
        reg_rdata{{ ckp }}[{{ idx }}]    <= {{ aw }}'h0;
    end
end
{% endfor %}

always_comb begin : NORM_REG_RDATA{{ ckp | upper }}
    norm_reg_rdata{{ ckp }} = {{ tpl_dict["common"]["reg_dw"] }}'b0;
    for ( integer i=0; i<{{ tpl_dict["common"]["grp_cnt"] }}; i=i+1 ) begin: NORM_REG_RDATA_BLK{{ ckp | upper }}
        norm_reg_rdata{{ ckp }} = norm_reg_rdata{{ ckp }} | reg_rdata{{ ckp }}[i];
    end
end

{% if tpl_dict["common"]["have_tbl"]==True %}
{% set m_name = tpl_dict["common"]["module_name"] %}
assign tbl_ack{{ ckp }}   = {{ m_name }}_cif_ack;
assign tbl_rdata{{ ckp }} = {{ "{" }}32{{ "{" }}{{ m_name }}_cif_ack {{ "}}" }} & {{ m_name }}_cif_rdata;
{% else %}
assign tbl_ack{{ ckp }}   = 1'b0;
assign tbl_rdata{{ ckp }} = 32'b0;
{% endif %}