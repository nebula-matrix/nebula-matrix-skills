{% set ckp          = tpl_dict["ck_domain"]                 %}
{% set clk          = tpl_dict["common"]["clk"]             %}
{% set rst          = tpl_dict["common"]["rst"]             %}
{% if tpl_dict["common"]["sync_rst"]==True  %}
{%     set sync_rst     = 1                 %}
{% else                                     %}
{%     set sync_rst     = 0                 %}
{% endif                                    %}
//========================================================
// CBB instance process
//========================================================
{% if tpl_dict["common"]["have_tbl"]==True %}
nbl_cti_top #(
    .CAH_NUM            ( {{ tpl_dict["tbl_inst_dict"]["cah_num"]           | lalign(5) }} ),
    .TBL_NUM            ( {{ tpl_dict["tbl_inst_dict"]["tbl_num"]           | lalign(5) }} ),
    .CIF_AW             ( {{ tpl_dict["tbl_inst_dict"]["aw"]                | lalign(5) }} ),
    .CIF_DW             ( {{ tpl_dict["tbl_inst_dict"]["dw"]                | lalign(5) }} ),
    .ATBL_ID            ( {{ tpl_dict["tbl_inst_dict"]["tbl_id"]            | lalign(tpl_dict["tbl_inst_dict"]["param_max_len"]) }} ),
    .ATBL_BADDR         ( {{ tpl_dict["tbl_inst_dict"]["tbl_baddr"]         | lalign(tpl_dict["tbl_inst_dict"]["param_max_len"]) }} ),
    .ATBL_ENTRY_DW      ( {{ tpl_dict["tbl_inst_dict"]["tbl_entry_dw"]      | lalign(tpl_dict["tbl_inst_dict"]["param_max_len"]) }} ),
    .ATBL_DP            ( {{ tpl_dict["tbl_inst_dict"]["tbl_dp"]            | lalign(tpl_dict["tbl_inst_dict"]["param_max_len"]) }} ),
    .ATBL_DP_AW         ( {{ tpl_dict["tbl_inst_dict"]["tbl_dp_aw"]         | lalign(tpl_dict["tbl_inst_dict"]["param_max_len"]) }} ),
    .TBL_MAX_DP_AW      ( {{ tpl_dict["tbl_inst_dict"]["tbl_max_dp_aw"]     | lalign(5) }} ),
    .ENTRY_MAX_DW_A32   ( {{ tpl_dict["tbl_inst_dict"]["tbl_max_dw_a32"]    | lalign(5) }} ),
    .ENTRY_MAX_AW_A2N   ( {{ tpl_dict["tbl_inst_dict"]["tbl_max_aw_a2n"]    | lalign(5) }} ),
    .END_OF_PARA_LIST   ( {{ "1" | lalign(5) }} )
) U_{{ tpl_dict["common"]["module_name"] | upper }}_TBL_PRO (
    .i_cif_req          ( {{ tpl_dict["tbl_inst_dict"]["cif_req"]       | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_cif_rw           ( {{ tpl_dict["tbl_inst_dict"]["cif_rw"]        | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_cif_addr         ( {{ tpl_dict["tbl_inst_dict"]["cif_addr"]      | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_cif_wdata        ( {{ tpl_dict["tbl_inst_dict"]["cif_wdata"]     | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_wr_ctrl          ( {{ tpl_dict["tbl_inst_dict"]["wr_ctrl"]       | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_cif_ack          ( {{ tpl_dict["tbl_inst_dict"]["cif_ack"]       | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_cif_rdata        ( {{ tpl_dict["tbl_inst_dict"]["cif_rdata"]     | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_cif_acc_hit      ( {{ tpl_dict["tbl_inst_dict"]["cif_acc_hit"]   | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_cif_ruerr        ( {{ tpl_dict["tbl_inst_dict"]["cif_ruerr"]     | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_cif_werr         ( {{ tpl_dict["tbl_inst_dict"]["cif_werr"]      | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_tbl_req          ( {{ tpl_dict["tbl_inst_dict"]["tbl_req"]       | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_tbl_rw           ( {{ tpl_dict["tbl_inst_dict"]["tbl_rw"]        | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_tbl_addr         ( {{ tpl_dict["tbl_inst_dict"]["tbl_addr"]      | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .o_tbl_wdata        ( {{ tpl_dict["tbl_inst_dict"]["tbl_wdata"]     | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_tbl_ack          ( {{ tpl_dict["tbl_inst_dict"]["tbl_ack"]       | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_tbl_rdata        ( {{ tpl_dict["tbl_inst_dict"]["tbl_rdata"]     | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_tbl_status       ( {{ tpl_dict["tbl_inst_dict"]["tbl_status"]    | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_clk              ( {{ (clk+ckp)                                  | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} ),
    .i_rst_n            ( {{ (rst+ckp)                                  | lalign(tpl_dict["tbl_inst_dict"]["max_conn_len"]) }} )
);

    {% for item_dict in tpl_dict["ro_tbl_inst_ls"] %}
cpu_ro_tbl_ctrl #(
    .ADDR_W             ( {{ item_dict["adw"]           | lalign(item_dict["ro_max_conn_len"]) }} ),
    .DATA_W             ( {{ item_dict["dw"]            | lalign(item_dict["ro_max_conn_len"]) }} ),
    .SYNC_RST           ( {{ sync_rst                   | lalign(item_dict["ro_max_conn_len"]) }} )
) U_RO_{{ item_dict["reg_name"] | upper }} (
    //---cpu access in interface---//
    .i_cpu_req          ( {{ item_dict["req"]           | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_rw           ( {{ item_dict["rw"]            | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_addr         ( {{ item_dict["offset_addr"]   | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_wdata        ( {{ item_dict["wdata"]         | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_ack          ( {{ item_dict["ack"]           | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_rdata        ( {{ item_dict["rdata"]         | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_status       ( {{ item_dict["status"]        | lalign(item_dict["ro_max_conn_len"]) }} ),
    //---cpu access out interface---//
    .o_cpu_ctrl_req     ( {{ item_dict["ctrl_req"]      | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_ctrl_rw      ( {{ item_dict["ctrl_rw"]       | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_ctrl_addr    ( {{ item_dict["ctrl_addr"]     | lalign(item_dict["ro_max_conn_len"]) }} ),
    .o_cpu_ctrl_wdata   ( {{ item_dict["ctrl_wdata"]    | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_ctrl_ack     ( {{ item_dict["ctrl_ack"]      | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_ctrl_rdata   ( {{ item_dict["ctrl_rdata"]    | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_cpu_ctrl_status  ( {{ item_dict["ctrl_status"]   | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_clk              ( {{ (clk+ckp)                  | lalign(item_dict["ro_max_conn_len"]) }} ),
    .i_rst_n            ( {{ (rst+ckp)                  | lalign(item_dict["ro_max_conn_len"]) }} )
);
    {% endfor %}
{% endif %}

{% if tpl_dict["common"]["have_wreg"]==True %}
    {% if tpl_dict["common"]["have_snap"]==True %}
        {% set snapshot_trig="i_snapshot_trig" %}
    {% else %}
        {% set snapshot_trig="1'b0" %}
    {% endif %}
nbl_ctwreg_top #(
    .CIF_AW             ( {{ tpl_dict["wreg_inst_dict"]["aw"]           | lalign(5) }} ),
    .CIF_DW             ( {{ tpl_dict["wreg_inst_dict"]["dw"]           | lalign(5) }} ),
    .PF_NUM             ( {{ tpl_dict["wreg_inst_dict"]["pf"]           | lalign(5) }} ),
    .RW_NUM             ( {{ tpl_dict["wreg_inst_dict"]["rw_num"]       | lalign(5) }} ),
    .RO_NUM             ( {{ tpl_dict["wreg_inst_dict"]["ro_num"]       | lalign(5) }} ),
    .SCTR_NUM           ( {{ tpl_dict["wreg_inst_dict"]["sctr_num"]     | lalign(5) }} ),
    .RCTR_NUM           ( {{ tpl_dict["wreg_inst_dict"]["rctr_num"]     | lalign(5) }} ),
    .MAX_DW_A32         ( {{ tpl_dict["wreg_inst_dict"]["max_dw_a32"]   | lalign(5) }} ),
    .AWREG_BADDR        ( {{ tpl_dict["wreg_inst_dict"]["baddr"]        | lalign(tpl_dict["wreg_inst_dict"]["wreg_param_max_len"]) }} ),
    .AWREG_EADDR        ( {{ tpl_dict["wreg_inst_dict"]["eaddr"]        | lalign(tpl_dict["wreg_inst_dict"]["wreg_param_max_len"]) }} ),
    .AWREG_DW           ( {{ tpl_dict["wreg_inst_dict"]["wreg_dw"]      | lalign(tpl_dict["wreg_inst_dict"]["wreg_param_max_len"]) }} ),
    .DEF_VAL            ( {{ tpl_dict["wreg_inst_dict"]["def_val"]      | lalign(tpl_dict["wreg_inst_dict"]["wreg_param_max_len"]) }} ),
    .END_OF_PARA_LIST   ( {{ "1" | lalign(5) }} )
) U_NBL_CTWREG_TOP (
    .i_cif_req           ( {{ tpl_dict["wreg_inst_dict"]["cif_req"]         | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_cif_rw            ( {{ tpl_dict["wreg_inst_dict"]["cif_rw"]          | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_cif_addr          ( {{ tpl_dict["wreg_inst_dict"]["cif_addr"]        | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_cif_wdata         ( {{ tpl_dict["wreg_inst_dict"]["cif_wdata"]       | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_wr_ctrl           ( {{ tpl_dict["wreg_inst_dict"]["wr_ctrl"]         | lalign( tpl_dict["wreg_inst_dict"]["wreg_ls_max_len"] ) }} ),   
    .i_reg_rctr_car      ( {{ tpl_dict["wreg_inst_dict"]["rctr_car"]        | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_reg_sctr_car      ( {{ tpl_dict["wreg_inst_dict"]["sctr_car"]        | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .o_cif_ack           ( {{ tpl_dict["wreg_inst_dict"]["cif_ack"]         | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .o_cif_rdata         ( {{ tpl_dict["wreg_inst_dict"]["cif_rdata"]       | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .o_rw_wreg_data      ( {{ tpl_dict["wreg_inst_dict"]["rw_data"]         | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_ro_wreg_data      ( {{ tpl_dict["wreg_inst_dict"]["ro_data"]         | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_snapshot_trig     ( {{ snapshot_trig                                 | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_sctr_inc_en       ( {{ tpl_dict["wreg_inst_dict"]["sctr_inc_en"]     | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_sctr_inc_num      ( {{ tpl_dict["wreg_inst_dict"]["sctr_inc_num"]    | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_sctr_sshot_mode_en( {{ tpl_dict["wreg_inst_dict"]["sctr_snap"]       | lalign( tpl_dict["wreg_inst_dict"]["wreg_ls_max_len"] ) }} ),   
    .i_rctr_inc_en       ( {{ tpl_dict["wreg_inst_dict"]["rctr_inc_en"]     | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_rctr_inc_num      ( {{ tpl_dict["wreg_inst_dict"]["rctr_inc_num"]    | lalign( tpl_dict["wreg_inst_dict"]["wreg_nor_max_len"] ) }} ),   
    .i_rctr_sshot_mode_en( {{ tpl_dict["wreg_inst_dict"]["rctr_snap"]       | lalign( tpl_dict["wreg_inst_dict"]["wreg_ls_max_len"] ) }} ),       
    .i_clk               ( {{ (clk+ckp)                                     | lalign( tpl_dict["wreg_inst_dict"]["wreg_ls_max_len"] ) }} ),   
    .i_rst_n             ( {{ (rst+ckp)                                     | lalign( tpl_dict["wreg_inst_dict"]["wreg_ls_max_len"] ) }} )   
);
{% endif %}

{% for item_dict in tpl_dict["inst_ls"] %}
    {% if   item_dict["rw_attr"] in ["sctr", "rctr"] %}
        {% if "inner_cif_err" in item_dict["i_inc_en"] %}
            {% set i_inc_en=("inner_cif_err"+ckp) %}
        {% else %}
            {% set i_inc_en=item_dict["i_inc_en"] %}
        {% endif %}
nbl_sshot_{{ item_dict["rw_attr"] }}_reg #(
    .CNT_W              ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .AW                 ( {{ item_dict["aw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .MAX_CNT            ( {{ item_dict["max_cnt"]       | lalign( item_dict["max_param_len"] ) }} ),
    .DEF_VAL            ( {{ item_dict["def_val"]       | lalign( item_dict["max_param_len"] ) }} ),
    .REG_ADDR           ( {{ item_dict["oft_addr"]      | lalign( item_dict["max_param_len"] ) }} ),
    .SYNC_RST           ( {{ sync_rst                   | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_reg_{{ item_dict["rw_attr"] }}_car     ( {{ item_dict["car_ctrl"]      | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wr_ctrl          ( {{ item_dict["wr_ctrl"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_snapshot_trig    ( {{ item_dict["snapshot_trig"] | lalign( item_dict["max_conn_len"] ) }} ),
    .i_sshot_mode_en    ( {{ item_dict["sshot_mode_en"] | lalign( item_dict["max_conn_len"] ) }} ),
    .i_ren              ( {{ item_dict["i_ren"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wen              ( {{ item_dict["i_wen"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_addr             ( {{ item_dict["i_addr"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wdata            ( {{ item_dict["i_wdata"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_inc_en           ( {{ i_inc_en                   | lalign( item_dict["max_conn_len"] ) }} ),
    .i_inc_num          ( {{ item_dict["i_inc_num"]     | lalign( item_dict["max_conn_len"] ) }} ),
    .o_cnt              ( {{ item_dict["o_cnt"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_clk              ( {{ (clk+ckp)                  | lalign( item_dict["max_conn_len"] ) }} ),
    .i_rst_n            ( {{ (rst+ckp)                  | lalign( item_dict["max_conn_len"] ) }} )   
);

    {% elif item_dict["rw_attr"] in ["rw", "wo"] %}
nbl_{{ item_dict["rw_attr"] }}_reg #(
    .DW             ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .AW             ( {{ item_dict["aw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .DEF_VAL        ( {{ item_dict["def_val"]       | lalign( item_dict["max_param_len"] ) }} ),
    .REG_ADDR       ( {{ item_dict["oft_addr"]      | lalign( item_dict["max_param_len"] ) }} ),
    .SYNC_RST       ( {{ sync_rst                   | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_wr_ctrl      ( {{ item_dict["wr_ctrl"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wen          ( {{ item_dict["i_wen"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_addr         ( {{ item_dict["i_addr"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wdata        ( {{ item_dict["i_wdata"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .o_data         ( {{ item_dict["o_data"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .clk            ( {{ (clk+ckp)                  | lalign( item_dict["max_conn_len"] ) }} ),
    .i_rst_n        ( {{ (rst+ckp)                  | lalign( item_dict["max_conn_len"] ) }} )
);

    {% elif item_dict["rw_attr"] == "rc" %}
nbl_{{ item_dict["rw_attr"] }}_reg #(
    .DW             ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .AW             ( {{ item_dict["aw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .DEF_VAL        ( {{ item_dict["def_val"]       | lalign( item_dict["max_param_len"] ) }} ),
    .REG_ADDR       ( {{ item_dict["oft_addr"]      | lalign( item_dict["max_param_len"] ) }} ),
    .SYNC_RST       ( {{ sync_rst                   | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_ren          ( {{ item_dict["i_ren"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_addr         ( {{ item_dict["i_addr"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_reg_rc_car   ( {{ item_dict["car_ctrl"]      | lalign( item_dict["max_conn_len"] ) }} ),
    .i_lgc_wen      ( {{ item_dict["i_lgc_wen"]     | lalign( item_dict["max_conn_len"] ) }} ),
    .i_lgc_data     ( {{ item_dict["i_lgc_data"]    | lalign( item_dict["max_conn_len"] ) }} ),
    .o_data         ( {{ item_dict["o_data"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .clk            ( {{ (clk+ckp)                  | lalign( item_dict["max_conn_len"] ) }} ),
    .i_rst_n        ( {{ (rst+ckp)                  | lalign( item_dict["max_conn_len"] ) }} )
);

    {% elif item_dict["rw_attr"] in ["rwc", "rww"] %}
nbl_{{ item_dict["rw_attr"] }}_reg #(
    .DW             ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .AW             ( {{ item_dict["aw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .DEF_VAL        ( {{ item_dict["def_val"]       | lalign( item_dict["max_param_len"] ) }} ),
    .REG_ADDR       ( {{ item_dict["oft_addr"]      | lalign( item_dict["max_param_len"] ) }} ),
    .SYNC_RST       ( {{ sync_rst                   | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_wr_ctrl      ( {{ item_dict["wr_ctrl"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wen          ( {{ item_dict["i_wen"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_addr         ( {{ item_dict["i_addr"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wdata        ( {{ item_dict["i_wdata"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_lgc_wen      ( {{ item_dict["i_lgc_wen"]     | lalign( item_dict["max_conn_len"] ) }} ),
    .i_lgc_data     ( {{ item_dict["i_lgc_data"]    | lalign( item_dict["max_conn_len"] ) }} ),
    .o_data         ( {{ item_dict["o_data"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .clk            ( {{ (clk+ckp)                  | lalign( item_dict["max_conn_len"] ) }} ),
    .i_rst_n        ( {{ (rst+ckp)                  | lalign( item_dict["max_conn_len"] ) }} )
);

    {% elif item_dict["rw_attr"] == "ro" %}
nbl_{{ item_dict["rw_attr"] }}_reg #(
    .DW             ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_data         ( {{ item_dict["i_lgc_data"]    | lalign( item_dict["max_conn_len"] ) }} ),
    .o_data         ( {{ item_dict["o_data"]        | lalign( item_dict["max_conn_len"] ) }} )
);

    {% elif item_dict["rw_attr"] in ["min", "max"] %}
nbl_{{ item_dict["rw_attr"] }}_reg #(
    .DW             ( {{ item_dict["dw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .AW             ( {{ item_dict["aw"]            | lalign( item_dict["max_param_len"] ) }} ),
    .REG_ADDR       ( {{ item_dict["oft_addr"]      | lalign( item_dict["max_param_len"] ) }} ),
    .SYNC_RST       ( {{ sync_rst                   | lalign( item_dict["max_param_len"] ) }} )
) U_{{ item_dict["reg_name"] | upper }}_{{ item_dict["field"] | upper }}{{ item_dict["idx"] }} (
    .i_reg_{{ item_dict["rw_attr"] }}_car  ( {{ item_dict["car_ctrl"]      | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wr_ctrl      ( {{ item_dict["wr_ctrl"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_ren          ( {{ item_dict["i_ren"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wen          ( {{ item_dict["i_wen"]         | lalign( item_dict["max_conn_len"] ) }} ),
    .i_addr         ( {{ item_dict["i_addr"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_wdata        ( {{ item_dict["i_wdata"]       | lalign( item_dict["max_conn_len"] ) }} ),
    .i_vld          ( {{ item_dict["i_lgc_vld"]     | lalign( item_dict["max_conn_len"] ) }} ),
    .i_data         ( {{ item_dict["i_lgc_data"]    | lalign( item_dict["max_conn_len"] ) }} ),
    .o_data         ( {{ item_dict["o_data"]        | lalign( item_dict["max_conn_len"] ) }} ),
    .i_clk          ( {{ (clk+ckp)                  | lalign( item_dict["max_conn_len"] ) }} ),
    .i_rst_n        ( {{ (rst+ckp)                  | lalign( item_dict["max_conn_len"] ) }} )
);

    {% endif %}
{% endfor %}