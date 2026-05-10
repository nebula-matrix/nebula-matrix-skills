{% set ckp          = tpl_dict["ck_domain"]                     %}
{% set clk          = tpl_dict["common"]["clk"]                 %}
{% set rst          = tpl_dict["common"]["rst"]                 %}
{% set mdl          = tpl_dict["common"]["module_name"] + ckp   %}
{% if tpl_dict["common"]["low_rst"]==True %}
    {% if tpl_dict["common"]["sync_rst"]==True %}
        {% set sync_rst     = 1 %}
        {% set alw_clk      = "always_ff @(posedge %s) begin"%(clk+ckp) %}
        {% set alw_rst_jud  = "if(~%s)begin"%(rst+ckp) %}
    {% else %}
        {% set sync_rst     = 0 %}
        {% set alw_clk      = "always_ff @(posedge %s or negedge %s) begin"%(clk+ckp, rst+ckp) %}
        {% set alw_rst_jud  = "if(~%s)begin"%(rst+ckp) %}
    {% endif %}
{% else %}
    {% if tpl_dict["common"]["sync_rst"]==True %}
        {% set sync_rst     = 1 %}
        {% set alw_clk      = "always_ff @(posedge %s) begin"%(clk+ckp) %}
        {% set alw_rst_jud  = "if(%s)begin"%(rst+ckp) %}
    {% else %}
        {% set sync_rst     = 0 %}
        {% set alw_clk      = "always_ff @(posedge %s or posedge %s) begin"%(clk+ckp, rst+ckp) %}
        {% set alw_rst_jud  = "if(%s)begin"%(rst+ckp) %}
    {% endif %}
{% endif %}
//========================================================
// main code {{ ckp }}
//========================================================
// req delay
{{ alw_clk }}
    {{ alw_rst_jud }}
        cif_{{ mdl }}_req_ff <= 1'b0;
    end
    else begin
        cif_{{ mdl }}_req_ff <= i_cif_{{ mdl }}_req;
    end
end

// normal register control
generate
for ( genvar j=0; j<{{ tpl_dict["common"]["grp_cnt"] }}; j=j+1 ) begin: GEN_{{ mdl | upper }}_NORM_REG_CTRL
{% if tpl_dict["common"]["fast_access"] ==True %}
    always_comb begin
        reg_wen{{ ckp }}[j] = i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff & ~i_cif_{{ mdl }}_rw;
        reg_ren{{ ckp }}[j] = i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff &  i_cif_{{ mdl }}_rw;
    end

    always_comb begin
        reg_addr{{ ckp }}[j]  = i_cif_{{ mdl }}_addr;
        reg_wdata{{ ckp }}[j] = i_cif_{{ mdl }}_wdata;
    end
{% else %}
    {{ alw_clk }}
        {{ alw_rst_jud }}
            reg_wen{{ ckp }}[j] <= 1'b0;
            reg_ren{{ ckp }}[j] <= 1'b0;
        end
        else begin
            reg_wen{{ ckp }}[j] <= i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff & ~i_cif_{{ mdl }}_rw;
            reg_ren{{ ckp }}[j] <= i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff &  i_cif_{{ mdl }}_rw;
        end
    end

    {{ alw_clk }}
        if( i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff ) begin
            reg_addr{{ ckp }}[j] <= i_cif_{{ mdl }}_addr;
        end
        else;
    end

    {{ alw_clk }}
        if( i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff & ~i_cif_{{ mdl }}_rw ) begin
            reg_wdata{{ ckp }}[j] <= i_cif_{{ mdl }}_wdata;
        end
        else;
    end
{% endif %}
end
endgenerate

{% if tpl_dict["common"]["have_tbl"]==True %}
assign access_tbl{{ ckp }}     = ( i_cif_{{ mdl }}_addr>={{ tpl_dict["common"]["reg_aw"] }}'h{{ tpl_dict["common"]["tbl_start_addr"] }} );
assign access_tbl_rsv{{ ckp }} = access_tbl{{ ckp }} & ~{{ mdl }}_access_hit;
{% else %}
assign access_tbl{{ ckp }}     = 1'b0;
assign access_tbl_rsv{{ ckp }} = access_tbl{{ ckp }};
{% endif %}
// fast access, ack process
{% if tpl_dict["common"]["fast_access"]==True %}
assign access_reg_ack_pre{{ ckp }} =i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff & ~access_tbl{{ ckp }};
{% else %}
{{ alw_clk }}
    {{ alw_rst_jud }}
        access_reg_ack_pre{{ ckp }} <= 1'b0;
    end
    else if ( i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff & ~access_tbl{{ ckp }} ) begin
        access_reg_ack_pre{{ ckp }} <= 1'b1;
    end
    else begin
        access_reg_ack_pre{{ ckp }} <= 1'b0;
    end
end
{% endif %}

{{ alw_clk }}
    {{ alw_rst_jud }}
        access_reg_ack{{ ckp }} <= 1'b0;
    end
    else if ( access_reg_ack_pre{{ ckp }} ) begin
        access_reg_ack{{ ckp }} <= 1'b1;
    end
    else begin
        access_reg_ack{{ ckp }} <= 1'b0;
    end
end

assign cif_{{ mdl }}_req_puls_ff[0] = i_cif_{{ mdl }}_req & ~cif_{{ mdl }}_req_ff;

{{ alw_clk }}
    {{ alw_rst_jud }}
        cif_{{ mdl }}_req_puls_ff[2:1] <= 2'b0;
    end
    else begin
        cif_{{ mdl }}_req_puls_ff[2:1] <= cif_{{ mdl }}_req_puls_ff[1:0];
    end
end

{{ alw_clk }}
    {{ alw_rst_jud }}
        access_tbl_rsv_ack{{ ckp }} <= 1'b0;
    end
    else if ( cif_{{ mdl }}_req_puls_ff[2] & access_tbl_rsv{{ ckp }} ) begin
        access_tbl_rsv_ack{{ ckp }} <= 1'b1;
    end
    else begin
        access_tbl_rsv_ack{{ ckp }} <= 1'b0;
    end
end

assign unify_reg_rdata{{ ckp }} = wide_reg_ack{{ ckp }} ? wide_reg_rdata{{ ckp }} : (|norm_reg_hit{{ ckp }} ? norm_reg_rdata{{ ckp }} : 32'hffff_ffff);
assign unify_tbl_rdata{{ ckp }} = ~access_tbl_rsv{{ ckp }} ? tbl_rdata{{ ckp }} : 32'hffff_ffff;
assign cif_ack_pre{{ ckp }}     = ( ~access_tbl{{ ckp }} & access_reg_ack{{ ckp }} ) | ( access_tbl{{ ckp }} & ( access_tbl_rsv_ack{{ ckp }} | tbl_ack{{ ckp }} ));
assign cif_rdata_pre{{ ckp }}   = ( ~access_tbl{{ ckp }} ? unify_reg_rdata{{ ckp }} : unify_tbl_rdata{{ ckp }});

{% if tpl_dict["common"]["fast_access"]==True %}
assign o_{{ mdl }}_cif_ack    = cif_ack_pre{{ ckp }};
assign o_{{ mdl }}_cif_rdata  = cif_rdata_pre{{ ckp }};
{% else %}
{{ alw_clk }}
    {{ alw_rst_jud }}
        o_{{ mdl }}_cif_ack <= 1'b0;
    end
    else begin
        o_{{ mdl }}_cif_ack <= cif_ack_pre{{ ckp }} & i_cif_{{ mdl }}_req;
    end
end

{{ alw_clk }}
    if ( cif_ack_pre{{ ckp }} ) begin
        o_{{ mdl }}_cif_rdata <= cif_rdata_pre{{ ckp }};
    end
    else;
end
{% endif %}

// process int
{% if tpl_dict["common"]["have_int"]==True %}
{{ alw_clk }}
    {{ alw_rst_jud }}
        o_reg_{{ mdl }}_interupt <= 1'b0;
    end
    else begin
        o_reg_{{ mdl }}_interupt <= |( {{ mdl }}_int_status_reg & ~{{ mdl }}_int_mask_reg );
    end
end
{% endif %}

//process tbl
{% if tpl_dict["common"]["have_tbl"]==True %}
assign cif_tbl_wr_err{{ ckp }} = {{ mdl }}_wr_err;
assign cif_ucor_err{{ ckp }}   = {{ mdl }}_ucor_err;
{% else %}
assign cif_tbl_wr_err{{ ckp }} = 1'b0;
assign cif_ucor_err{{ ckp }}   = 1'b0;
{% endif %}

//process wreg
assign cif_wide_reg_wr_err{{ ckp }} = 1'b0;

//process err
assign cif_wr_err{{ ckp }}       = cif_tbl_wr_err{{ ckp }} | cif_wide_reg_wr_err{{ ckp }};
assign inner_cif_err{{ ckp }}    = cif_ucor_err{{ ckp }} | cif_wr_err{{ ckp }};

{% if tpl_dict["common"]["have_cif_err_int"]==True %}
{% set gap          = 30 - tpl_dict["common"]["reg_aw"] %}
{% set reg_dw       = tpl_dict["common"]["reg_dw"] %}
{% set err_event    = "inner_cif_err" + ckp %}
{% set err_info     = "{cif_ucor_err%s, cif_wr_err%s, "%(ckp, ckp) + "%d'b0, "%(gap) + "i_cif_%s_addr}"%(mdl) %}
{% set int_state    = "%s_int_status_cif_err"%(mdl) %}
{% set reg_err_info = "{cif_err_info_ucor_err%s, cif_err_info_wr_err%s, cif_err_info_addr%s}"%(ckp, ckp, ckp) %}
err_info_reg #(
    .SYNC_RST           ( {{ sync_rst       | lalign(10) }} ),
    .INFO_W             ( {{ reg_dw         | lalign(10) }} )
) U_{{ mdl | upper }}_CIF_ERR_INFO_REG (
    .err_event          ( {{ err_event      | lalign( 90 ) }} ),
    .err_info           ( {{ err_info       | lalign( 90 ) }} ),
    .int_state          ( {{ int_state      | lalign( 90 ) }} ),
    .o_reg_err_info     ( {{ reg_err_info   | lalign( 90 ) }} ),
    .clk                ( {{ ( clk + ckp )  | lalign( 90 ) }} ),
    .i_rst_n            ( {{ ( rst + ckp )  | lalign( 90 ) }} )
);
{% endif %}